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
        raise NotImplementedError("TODO Ex1: send the houses of the catalog as buttons follow:<house>")

    def follow(self, call, house):
        raise NotImplementedError("TODO Ex1: read or create the user, add the house, POST /users, confirm to the chat")

    # --- Ex2: /houses, rooms, room view ---
    def on_houses(self, message):
        raise NotImplementedError("TODO Ex2: send the houses followed by this user as buttons house:<house>")

    def show_rooms(self, chat_id, house):
        raise NotImplementedError("TODO Ex2: GET /houses/<house> and send the rooms as buttons room:<house>:<room>")

    def show_room(self, chat_id, house, room):
        raise NotImplementedError("TODO Ex2: thresholds from the catalog, measurements and HVAC from the device connector, buttons set:<house>:<room>:<key>")

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
        raise NotImplementedError("TODO Ex3: parse the number, PUT the threshold, handle 400 and unreachable catalog, forget the waiting state on success")

    # --- Ex4: MQTT alerts ---
    def notify(self, topic, payload):
        raise NotImplementedError("TODO Ex4: send the alert to every user who follows the house; one failed send must not stop the others")


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
