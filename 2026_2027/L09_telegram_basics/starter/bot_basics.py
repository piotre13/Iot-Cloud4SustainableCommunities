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
        raise NotImplementedError("TODO Ex1: send a welcome message with the first name of the user")

    def on_help(self, message):
        raise NotImplementedError("TODO Ex1: send the list of commands")

    def on_text(self, message):
        raise NotImplementedError("TODO Ex1: repeat the received text")

    # --- Ex2: inline keyboard ---
    def on_hvac(self, message):
        raise NotImplementedError("TODO Ex2: send a message with an inline keyboard: buttons ON and OFF (callback_data hvac:ON / hvac:OFF)")

    def on_temp(self, message):
        raise NotImplementedError("TODO Ex2: reply with a random temperature")

    def on_button(self, call):
        raise NotImplementedError("TODO Ex2: answer the callback query and reply HVAC switched <ON|OFF> (simulated)")


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
