"""ThingSpeak adaptor and Telegram bot without network access to ThingSpeak or Telegram (dry run).

Run from smart_home/:  python -m tests.test_s3_dry_run

Real mosquitto + catalog + one device connector. The bot is a real telebot.TeleBot with a fake token:
updates are fed by hand and send_message is captured, so handler routing is the real one.
"""
import json
import tempfile
import time
from pathlib import Path

import requests
import telebot

from common.mymqtt import MyMQTT
from common.senml import senml_record
from telegram_bot.service import SmartHomeBot
from tests.test_catalog import PORT as CATALOG_PORT, URL as CATALOG
from tests.test_common import MQTT_PORT, start_broker
from tests.test_e2e import SEED, spawn, start_connector, wait_until
from thingspeak_adaptor.service import ThingSpeakAdaptor

ADA, BOB = 1001, 1002


def user_json(chat_id, name):
    return {"id": chat_id, "is_bot": False, "first_name": name}


def message_update(chat_id, name, text):
    msg = {"message_id": 1, "date": 0, "chat": {"id": chat_id, "type": "private"},
           "from": user_json(chat_id, name), "text": text}
    if text.startswith("/"):
        msg["entities"] = [{"type": "bot_command", "offset": 0, "length": len(text)}]
    return telebot.types.Update.de_json({"update_id": 1, "message": msg})


def button_update(chat_id, name, data):
    msg = {"message_id": 1, "date": 0, "chat": {"id": chat_id, "type": "private"}, "text": "menu"}
    return telebot.types.Update.de_json({"update_id": 1, "callback_query": {
        "id": "1", "from": user_json(chat_id, name), "chat_instance": "x", "data": data, "message": msg}})


class Outbox:
    """Replaces bot.send_message: keeps (chat_id, text, button callback_data list)."""

    def __init__(self):
        self.sent = []

    def send_message(self, chat_id, text, reply_markup=None, **kwargs):
        buttons = [b.callback_data for row in reply_markup.keyboard for b in row] if reply_markup else []
        self.sent.append((chat_id, text, buttons))

    def last(self):
        return self.sent[-1]


def check_adaptor():
    adaptor = ThingSpeakAdaptor(CATALOG)  # no key -> dry run
    adaptor.refresh_fields()
    assert adaptor.fields["house1/kitchen/temperature"] == 1
    adaptor.notify("smarthome/house1/kitchen/temperature", senml_record("x", "x", "", 20.0))
    adaptor.notify("smarthome/house1/kitchen/temperature", senml_record("x", "x", "", 21.5))  # only the latest is kept
    adaptor.notify("smarthome/house1/bedroom/humidity", senml_record("x", "x", "", 55))
    adaptor.notify("smarthome/house1/kitchen/hvac/state", {"state": "ON"})
    adaptor.notify("smarthome/house2/bedroom/temperature", senml_record("x", "x", "", 30))  # not mapped: ignored
    assert adaptor.upload() == {"field1": 21.5, "field3": 1, "field5": 55}
    assert adaptor.upload() is None  # nothing new, nothing sent

    # a new mapping in the catalog is used after refresh, no restart
    ts = requests.get(f"{CATALOG}/thingspeak").json()
    ts["fields"]["house2/bedroom/temperature"] = 7
    requests.put(f"{CATALOG}/thingspeak", json=ts).raise_for_status()
    adaptor.refresh_fields()
    adaptor.notify("smarthome/house2/bedroom/temperature", senml_record("x", "x", "", 30))
    assert adaptor.upload() == {"field7": 30}

    # a failed upload keeps the values for the next round (fake key, ThingSpeak answer simulated)
    import thingspeak_adaptor.service as ts_module
    real_get = ts_module.requests.get
    ts_module.requests.get = lambda *a, **k: type("R", (), {"text": "0", "raise_for_status": lambda self: None})()
    adaptor.write_key = "fake"
    adaptor.notify("smarthome/house1/kitchen/temperature", senml_record("x", "x", "", 19.0))
    adaptor.upload()
    ts_module.requests.get = real_get
    adaptor.write_key = None
    assert adaptor.pending == {1: 19.0}
    assert adaptor.upload() == {"field1": 19.0}

    # over MQTT, from the real device connector
    adaptor.mqtt = MyMQTT("ts_test", "localhost", MQTT_PORT, notifier=adaptor)
    adaptor.mqtt.start()
    adaptor.mqtt.subscribe("smarthome/+/+/temperature")
    adaptor.mqtt.subscribe("smarthome/+/+/hvac/state")
    time.sleep(0.5)
    requests.put("http://localhost:8181/hvac", json={"command": "ON"}).raise_for_status()
    wait_until(lambda: adaptor.pending.get(3) == 1, what="HVAC state from the connector")
    adaptor.mqtt.stop()
    print("adaptor: ok")


def check_bot():
    bot = telebot.TeleBot("123456:fake-token-for-tests", threaded=False)
    out = Outbox()
    bot.send_message = out.send_message
    bot.answer_callback_query = lambda *a, **k: None
    app = SmartHomeBot(bot, CATALOG)

    def feed(update):
        bot.process_new_updates([update])

    feed(message_update(ADA, "Ada", "/houses"))
    assert "/start" in out.last()[1]
    feed(message_update(ADA, "Ada", "/start"))
    assert out.last()[2] == ["follow:house1", "follow:house2"]
    feed(button_update(ADA, "Ada", "follow:house1"))
    feed(button_update(BOB, "Bob", "follow:house2"))
    users = {u["chat_id"]: u for u in requests.get(f"{CATALOG}/users").json()}
    assert users[ADA] == {"chat_id": ADA, "name": "Ada", "houses": ["house1"]}

    feed(message_update(ADA, "Ada", "/houses"))
    assert out.last()[2] == ["house:house1"]
    feed(button_update(ADA, "Ada", "house:house1"))
    assert out.last()[2] == ["room:house1:kitchen", "room:house1:bedroom"]
    feed(button_update(ADA, "Ada", "room:house1:kitchen"))
    chat, text, buttons = out.last()
    assert "temperature:" in text and "HVAC: ON" in text and "t_min 19" in text, text
    assert buttons == ["set:house1:kitchen:t_min", "set:house1:kitchen:t_max", "set:house1:kitchen:h_max"]
    feed(button_update(ADA, "Ada", "room:house1:bedroom"))
    assert "device connector offline" in out.last()[1]

    # change a threshold: button, then the value as a plain message
    feed(button_update(ADA, "Ada", "set:house1:kitchen:t_min"))
    feed(message_update(ADA, "Ada", "abc"))
    assert "number" in out.last()[1]
    feed(message_update(ADA, "Ada", "30"))  # above t_max 23: refused by the catalog, still waiting
    assert "Not accepted" in out.last()[1]
    feed(message_update(ADA, "Ada", "20,5"))
    assert requests.get(f"{CATALOG}/houses/house1/kitchen/thresholds").json()["t_min"] == 20.5
    feed(message_update(ADA, "Ada", "hello"))
    assert "Commands" in out.last()[1]

    # alerts only to the users of that house
    out.sent.clear()
    def flaky_send(chat_id, text, **kwargs):  # Bob blocked the bot: Ada must still get alerts
        if chat_id == BOB:
            raise RuntimeError("Forbidden: bot was blocked by the user")
        out.send_message(chat_id, text, **kwargs)
    bot.send_message = flaky_send
    requests.post(f"{CATALOG}/users", json={"chat_id": BOB, "name": "Bob", "houses": ["house1", "house2"]})
    app.notify("smarthome/house1/alerts", {"room": "kitchen", "msg": "humidity 78% > 70%"})
    assert out.sent == [(ADA, "ALERT house1/kitchen: humidity 78% > 70%", [])]
    print("bot: ok")


def main():
    procs = []
    with tempfile.TemporaryDirectory() as tmp:
        state = json.loads(SEED.read_text())
        state["broker"]["port"] = MQTT_PORT
        (Path(tmp) / "state.json").write_text(json.dumps(state))
        try:
            procs.append(start_broker())
            procs.append(spawn("catalog.service", str(CATALOG_PORT), str(Path(tmp) / "state.json")))
            wait_until(lambda: requests.get(f"{CATALOG}/broker", timeout=1).ok, what="catalog")
            procs.append(start_connector("house1", "kitchen", 8181))
            check_adaptor()
            check_bot()
        finally:
            for p in reversed(procs):
                p.terminate()
                p.wait()
    print("s3 dry run: all checks passed")


if __name__ == "__main__":
    main()
