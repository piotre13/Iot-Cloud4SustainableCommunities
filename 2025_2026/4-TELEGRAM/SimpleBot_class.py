import time

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup


class SimpleBot:
    def __init__(self, token):
        self.token = token
        self.bot = telepot.Bot(self.token)
        self.callback_dict = {
            "chat": self.on_chat_message,
            "callback_query": self.on_callback_query,
        }

        MessageLoop(self.bot, self.callback_dict).run_as_thread()

    def on_chat_message(self, msg):
        print(msg)
        content_type, chat_type, chat_ID = telepot.glance(msg)
        if content_type == "text":
            if msg["text"] == "\start":
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="devices", callback_data="dev")],
                        [InlineKeyboardButton(text="houses", callback_data="hous")],
                    ]
                )

                self.bot.sendMessage(
                    chat_ID, "These are the possible services", reply_markup=keyboard
                )

            self.bot.sendMessage(chat_ID, f"i like your message{msg['text']}")

    def on_callback_query(self, msg):
        print(msg)
        query_id, ch_id, query = telepot.glance(msg, flavor="callback_query")
        if query == "dev":
            # get request to catalog
            data = {"device1": "on", "device2": "off"}
            self.bot.sendMessage(ch_id, f"these are the devices {data}")
        pass


if __name__ == "__main__":
    token = "<your_token>"
    bot = SimpleBot(token)
    while True:
        time.sleep(3)
