"""Telegram bot basics with pyTelegramBotAPI (telebot).

Run from this folder:   python bot_basics.py
Needs TELEGRAM_TOKEN in 2026_2027/.env (create the bot with @BotFather).

/start  welcome        /help  list of commands
/hvac   two buttons ON / OFF (simulated)        /temp  a random temperature
any other text is echoed back
"""
import os
import random
import sys
from pathlib import Path

import telebot
from dotenv import load_dotenv
from telebot import types

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"  # 2026_2027/.env


def get_secret(name):
    """Read a secret from 2026_2027/.env (or the environment). None if missing."""
    load_dotenv(ENV_PATH)
    return os.getenv(name) or None


class EchoBot:
    def __init__(self, bot):
        self.bot = bot
        bot.register_message_handler(self.on_start, commands=["start"])
        bot.register_message_handler(self.on_help, commands=["help"])
        bot.register_message_handler(self.on_hvac, commands=["hvac"])
        bot.register_message_handler(self.on_temp, commands=["temp"])
        bot.register_message_handler(self.on_text, content_types=["text"])  # after the commands
        bot.register_callback_query_handler(self.on_button, func=lambda call: True)

    # --- Ex1: commands and echo ---
    def on_start(self, message):
        self.bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}! Send /help to see what I can do.")

    def on_help(self, message):
        self.bot.send_message(message.chat.id, "/start - welcome\n/help - this text\n/hvac - switch the HVAC\n"
                                               "/temp - read the temperature\nAnything else: I repeat it.")

    def on_text(self, message):
        self.bot.send_message(message.chat.id, f"You said: {message.text}")

    # --- Ex2: inline keyboard ---
    def on_hvac(self, message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ON", callback_data="hvac:ON"),
                   types.InlineKeyboardButton("OFF", callback_data="hvac:OFF"))
        self.bot.send_message(message.chat.id, "HVAC:", reply_markup=markup)

    def on_temp(self, message):
        self.bot.send_message(message.chat.id, f"Temperature: {random.uniform(18, 26):.1f} C (random)")

    def on_button(self, call):
        self.bot.answer_callback_query(call.id)  # stops the spinner on the button
        action, value = call.data.split(":")
        if action == "hvac":
            self.bot.send_message(call.message.chat.id, f"HVAC switched {value} (simulated)")


def main():
    token = get_secret("TELEGRAM_TOKEN")
    if token is None:
        sys.exit("TELEGRAM_TOKEN missing: copy 2026_2027/.env.example to 2026_2027/.env and write your bot token in it")
    bot = telebot.TeleBot(token)
    EchoBot(bot)
    print("Bot running, Ctrl+C to stop")
    bot.infinity_polling()


if __name__ == "__main__":
    main()
