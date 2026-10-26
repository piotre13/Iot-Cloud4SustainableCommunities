"""Offline test of telegram_bot.py: no Telegram, no token.

Needs a running system (see README, "Test without Telegram"): broker, catalog, one connector house1/kitchen.
Usage:  python check_bot.py [--catalog http://localhost:8080]
The bot is a real telebot.TeleBot with a fake token: updates are fed by hand and send_message is recorded.
"""
import argparse
import time

import requests
import telebot

from config import get_broker
from mymqtt import MyMQTT
from telegram_bot import SmartHomeBot

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="http://localhost:8080")
    args = parser.parse_args()
    catalog = args.catalog

    bot = telebot.TeleBot("123456:fake-token-for-tests", threaded=False)
    out = Outbox()
    bot.send_message = out.send_message
    bot.answer_callback_query = lambda *a, **k: None
    app = SmartHomeBot(bot, catalog)

    def feed(update):
        bot.process_new_updates([update])

    # Ex1
    feed(message_update(ADA, "Ada", "/houses"))
    assert "/start" in out.last()[1]
    feed(message_update(ADA, "Ada", "/start"))
    assert out.last()[2] == ["follow:house1", "follow:house2"]
    feed(button_update(ADA, "Ada", "follow:house1"))
    feed(button_update(BOB, "Bob", "follow:house2"))
    users = {u["chat_id"]: u for u in requests.get(f"{catalog}/users").json()}
    assert users[ADA] == {"chat_id": ADA, "name": "Ada", "houses": ["house1"]}
    print("Ex1 ok")

    # Ex2
    feed(message_update(ADA, "Ada", "/houses"))
    assert out.last()[2] == ["house:house1"]
    feed(button_update(ADA, "Ada", "house:house1"))
    assert out.last()[2] == ["room:house1:kitchen", "room:house1:bedroom"]
    feed(button_update(ADA, "Ada", "room:house1:kitchen"))
    chat, text, buttons = out.last()
    assert "no data yet" in text and "t_min" in text, text  # nothing received over MQTT so far
    assert buttons == ["set:house1:kitchen:t_min", "set:house1:kitchen:t_max", "set:house1:kitchen:h_max"]
    app.latest[("house1", "kitchen")] = {"temperature": {"bn": "x", "bt": time.time(), "e": [{"n": "temperature", "u": "Cel", "t": 0, "v": 21.4}]},
                                         "hvac": "ON"}  # what notify (Ex4) stores
    feed(button_update(ADA, "Ada", "room:house1:kitchen"))
    text = out.last()[1]
    assert "temperature: 21.4 Cel" in text and "HVAC: ON" in text and "t_min" in text, text
    app.latest.clear()
    print("Ex2 ok")

    # Ex3: button, then the value as a plain message
    t_max = requests.get(f"{catalog}/houses/house1/kitchen/thresholds").json()["t_max"]
    feed(button_update(ADA, "Ada", "set:house1:kitchen:t_min"))
    feed(message_update(ADA, "Ada", "abc"))
    assert "number" in out.last()[1]
    feed(message_update(ADA, "Ada", str(t_max + 10)))  # above t_max: refused by the catalog, still waiting
    assert "Not accepted" in out.last()[1]
    feed(message_update(ADA, "Ada", "20,5"))
    assert requests.get(f"{catalog}/houses/house1/kitchen/thresholds").json()["t_min"] == 20.5
    feed(message_update(ADA, "Ada", "hello"))
    assert "Commands" in out.last()[1]
    print("Ex3 ok")

    # Ex4: alerts only to the followers; Bob "blocked" the bot but Ada still gets hers
    out.sent.clear()

    def flaky_send(chat_id, text, **kwargs):
        if chat_id == BOB:
            raise RuntimeError("Forbidden: bot was blocked by the user")
        out.send_message(chat_id, text, **kwargs)
    bot.send_message = flaky_send
    requests.post(f"{catalog}/users", json={"chat_id": BOB, "name": "Bob", "houses": ["house1", "house2"]})
    app.notify("smarthome/house1/alerts", {"room": "kitchen", "msg": "humidity 78% > 70%"})
    assert out.sent == [(ADA, "ALERT house1/kitchen: humidity 78% > 70%", [])]

    # the same through a real broker
    out.sent.clear()
    broker = get_broker(catalog)
    app.mqtt = MyMQTT("check_bot", broker["host"], broker["port"], notifier=app)
    app.mqtt.start()
    app.mqtt.subscribe("smarthome/+/alerts")
    time.sleep(0.5)
    app.mqtt.publish("smarthome/house2/alerts", {"room": "bedroom", "msg": "humidity 90% > 70%"})
    app.mqtt.publish("smarthome/house1/alerts", {"room": "kitchen", "msg": "humidity 80% > 70%"})
    end = time.time() + 5
    while len(out.sent) < 1 and time.time() < end:
        time.sleep(0.1)
    time.sleep(0.5)
    app.mqtt.stop()
    assert out.sent == [(ADA, "ALERT house1/kitchen: humidity 80% > 70%", [])], out.sent

    # measurements and HVAC state are remembered, per room
    app.notify("smarthome/house1/kitchen/temperature", {"bn": "x", "bt": time.time(), "e": [{"n": "temperature", "u": "Cel", "t": 0, "v": 18.5}]})
    app.notify("smarthome/house1/kitchen/hvac/state", {"state": "OFF"})
    out.sent.clear()
    feed(button_update(ADA, "Ada", "room:house1:kitchen"))
    text = out.last()[1]
    assert "temperature: 18.5 Cel" in text and "HVAC: OFF" in text, text
    feed(button_update(ADA, "Ada", "room:house1:bedroom"))
    assert "no data yet" in out.last()[1]  # another room: untouched
    print("Ex4 ok")
    print("bot: all checks passed")


if __name__ == "__main__":
    main()
