"""Telegram bot (pyTelegramBotAPI / telebot): browse houses, read the latest measurements,
change thresholds, receive humidity alerts.

Run:  python telegram_bot.py [--catalog URL]
Needs TELEGRAM_TOKEN in 2026_2027/.env (create the bot with @BotFather).

/start   choose the houses you follow (saved in the catalog: POST /users)
/houses  house -> room -> latest measurements, HVAC state, thresholds -> buttons to change them
Alerts from smarthome/+/alerts go to the users who follow that house.
"""
import argparse
import sys

import requests
import telebot
from telebot import types

from config import catalog_url, get_broker, get_secret
from mymqtt import MyMQTT

THRESHOLD_KEYS = ("t_min", "t_max", "h_max")


def keyboard(buttons):
    """buttons: list of (text, callback_data), one per row."""
    markup = types.InlineKeyboardMarkup()
    for text, data in buttons:
        markup.add(types.InlineKeyboardButton(text, callback_data=data))
    return markup


class SmartHomeBot:
    def __init__(self, bot, catalog):
        self.bot = bot
        self.catalog = catalog
        self.waiting_value = {}  # chat_id -> (house, room, key) while we wait for a number
        self.mqtt = None
        bot.register_message_handler(self.on_start, commands=["start"])
        bot.register_message_handler(self.on_houses, commands=["houses"])
        bot.register_message_handler(self.on_text, content_types=["text"])
        bot.register_callback_query_handler(self.on_button, func=lambda call: True)

    # --- catalog helpers ---
    def get(self, path):
        r = requests.get(f"{self.catalog}{path}", timeout=5)
        r.raise_for_status()
        return r.json()

    def get_user(self, chat_id):
        return next((u for u in self.get("/users") if u["chat_id"] == chat_id), None)

    # --- Ex1: /start and follow ---
    def on_start(self, message):
        houses = [h["house_id"] for h in self.get("/houses")]
        self.bot.send_message(message.chat.id, "Which houses do you want to follow?",
                              reply_markup=keyboard([(h, f"follow:{h}") for h in houses]))

    def follow(self, call, house):
        chat_id = call.message.chat.id
        user = self.get_user(chat_id) or {"chat_id": chat_id, "name": call.from_user.first_name, "houses": []}
        if house not in user["houses"]:
            user["houses"].append(house)
        requests.post(f"{self.catalog}/users", json=user, timeout=5).raise_for_status()
        self.bot.send_message(chat_id, f"You follow: {', '.join(user['houses'])}. Now try /houses")

    # --- Ex2: /houses, rooms, room view ---
    def on_houses(self, message):
        user = self.get_user(message.chat.id)
        if user is None or not user["houses"]:
            self.bot.send_message(message.chat.id, "You follow no house yet: send /start")
            return
        self.bot.send_message(message.chat.id, "Choose a house",
                              reply_markup=keyboard([(h, f"house:{h}") for h in user["houses"]]))

    def show_rooms(self, chat_id, house):
        rooms = [r["room_id"] for r in self.get(f"/houses/{house}")["rooms"]]
        self.bot.send_message(chat_id, f"{house}: choose a room",
                              reply_markup=keyboard([(r, f"room:{house}:{r}") for r in rooms]))

    def show_room(self, chat_id, house, room):
        thresholds = self.get(f"/houses/{house}/{room}/thresholds")
        lines = [f"{house}/{room}"]
        try:
            device = self.get(f"/devices/dc_{house}_{room}")
            status = requests.get(f"{device['rest_url']}/", timeout=3).json()
            lines += [f"{m['e'][0]['n']}: {m['e'][0]['v']} {m['e'][0]['u']}" for m in status["measurements"]]
            lines.append(f"HVAC: {status['hvac']}")
        except requests.RequestException:  # no connector registered for the room, or not running
            lines.append("device connector offline")
        lines.append("thresholds: " + ", ".join(f"{k} {v}" for k, v in thresholds.items()))
        self.bot.send_message(chat_id, "\n".join(lines), reply_markup=keyboard(
            [(f"change {k}", f"set:{house}:{room}:{k}") for k in THRESHOLD_KEYS]))

    # --- all the buttons come here ---
    def on_button(self, call):
        self.bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        action, *args = call.data.split(":")
        if action == "follow":
            self.follow(call, args[0])
        elif action == "house":
            self.show_rooms(chat_id, args[0])
        elif action == "room":
            self.show_room(chat_id, *args)
        elif action == "set":
            house, room, key = args
            self.waiting_value[chat_id] = (house, room, key)
            self.bot.send_message(chat_id, f"Send the new value of {key} for {house}/{room}")

    # --- Ex3: the new value arrives as a plain message ---
    def on_text(self, message):
        """A plain message is the new value of a threshold, if we asked for one."""
        chat_id = message.chat.id
        if chat_id not in self.waiting_value:
            self.bot.send_message(chat_id, "Commands: /start, /houses")
            return
        house, room, key = self.waiting_value[chat_id]
        try:
            value = float(message.text.replace(",", "."))
        except ValueError:
            self.bot.send_message(chat_id, f"Please send a number for {key}")
            return
        try:
            r = requests.put(f"{self.catalog}/houses/{house}/{room}/thresholds", json={key: value}, timeout=5)
        except requests.RequestException:
            self.bot.send_message(chat_id, "Catalog unreachable, try again")
            return
        if r.status_code == 400:
            self.bot.send_message(chat_id, "Not accepted: thresholds must be numbers with t_min < t_max. Send another value")
            return
        r.raise_for_status()
        del self.waiting_value[chat_id]
        self.bot.send_message(chat_id, f"{house}/{room}: {key} = {value:g}")

    # --- Ex4: MQTT alerts ---
    def notify(self, topic, payload):
        house = topic.split("/")[1]
        text = f"ALERT {house}/{payload['room']}: {payload['msg']}"
        for user in self.get("/users"):
            if house in user["houses"]:
                try:
                    self.bot.send_message(user["chat_id"], text)
                except Exception as e:  # e.g. this user blocked the bot: the others still get the alert
                    print(f"Alert not delivered to {user['chat_id']}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Smart home Telegram bot")
    parser.add_argument("--catalog", default=None, help="catalog URL (default: settings.json)")
    args = parser.parse_args()
    catalog = args.catalog or catalog_url()

    token = get_secret("TELEGRAM_TOKEN")
    if token is None:
        sys.exit("TELEGRAM_TOKEN missing: copy 2026_2027/.env.example to .env and add your bot token")

    app = SmartHomeBot(telebot.TeleBot(token), catalog)
    broker = get_broker(catalog)
    app.mqtt = MyMQTT("telegram_bot", broker["host"], broker["port"], notifier=app)
    app.mqtt.start()
    app.mqtt.subscribe("smarthome/+/alerts")
    print("Bot running, Ctrl+C to stop")
    try:
        app.bot.infinity_polling()
    finally:
        app.mqtt.stop()


if __name__ == "__main__":
    main()
