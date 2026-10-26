"""REFERENCE ONLY: the same bot as bot_basics.py, written with telepot.

telepot is no longer maintained (last release 2019): you may see it in old tutorials and old code,
but new projects use pyTelegramBotAPI (telebot). Compare it line by line with bot_basics.py.
Do not run it: it needs a real token and telepot may break on new Python versions.
"""
import random
import time

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup


class TelepotBot:
    def __init__(self, token):
        self.bot = telepot.Bot(token)
        # telebot: handlers are registered one by one (commands=..., content_types=...).
        # telepot: ONE function per "flavor" (chat, callback_query); we must look at the text ourselves.
        handlers = {"chat": self.on_chat_message, "callback_query": self.on_callback_query}
        MessageLoop(self.bot, handlers).run_as_thread()  # telebot: bot.infinity_polling()

    def on_chat_message(self, msg):
        # glance() extracts the useful fields from the raw dict (telebot gives you message.chat.id etc.)
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type != "text":
            return
        text = msg["text"]
        if text == "/start":  # the old example had "\start" (a backslash is a typo: commands start with "/")
            name = msg["from"]["first_name"]
            self.bot.sendMessage(chat_id, f"Hello {name}! Send /help to see what I can do.")
        elif text == "/help":
            self.bot.sendMessage(chat_id, "/start - welcome\n/help - this text\n/hvac - switch the HVAC\n"
                                          "/temp - read the temperature\nAnything else: I repeat it.")
        elif text == "/hvac":
            # telepot keyboards are built from plain lists: a list of rows, each row a list of buttons
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="ON", callback_data="hvac:ON"),
                InlineKeyboardButton(text="OFF", callback_data="hvac:OFF"),
            ]])
            self.bot.sendMessage(chat_id, "HVAC:", reply_markup=keyboard)
        elif text == "/temp":
            self.bot.sendMessage(chat_id, f"Temperature: {random.uniform(18, 26):.1f} C (random)")
        else:  # the old example also echoed after /start: here the branches exclude each other
            self.bot.sendMessage(chat_id, f"You said: {text}")

    def on_callback_query(self, msg):
        # for a button press glance() needs flavor="callback_query" and returns (query_id, from_id, data)
        query_id, from_id, data = telepot.glance(msg, flavor="callback_query")
        self.bot.answerCallbackQuery(query_id)  # telebot: answer_callback_query
        action, value = data.split(":")
        if action == "hvac":
            # in a private chat the chat id equals the user id (from_id); in groups use msg["message"]["chat"]["id"]
            chat_id = msg["message"]["chat"]["id"]
            self.bot.sendMessage(chat_id, f"HVAC switched {value} (simulated)")


if __name__ == "__main__":
    TelepotBot("<your_token>")
    while True:  # MessageLoop runs in a thread: keep the main thread alive
        time.sleep(3)
