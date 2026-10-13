import telepot
import telepot.Bot as Bot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup


class SimpleBot:
    def __init__(self, token):
        self.token = token
        self.bot = Bot(self.token)
        self.callback_dict = {
            "chat": self.on_chat_message,
            "callback_query": self.on_query_message,
        }
        MessageLoop(self.bot, self.callback_dict).run_as_thread()

    def on_chat_message(self, msg):
        # read the message and extract information such as the chat id
        content_type, chat_type, chat_ID = telepot.glance(msg)
        # based on content_type and on the content you can react on that
        # e.g.
        if content_type == "text":
            if msg["text"] == "\start":  # here is stored the actual content
                # DO something etc..
                # simple message reply
                self.bot.sendMessage(chat_ID, "Starting!")

                # reply with a keyboard
            elif msg["text"] == "/devices":
                in_line_k_buttons = [
                    [
                        InlineKeyboardButton(text=" device1", callback_data="d1"),
                        InlineKeyboardButton(text="device2", callback_data="d2"),
                    ]
                ]
                keyboard = InlineKeyboardMarkup(inline_keyboard=in_line_k_buttons)
                self.bot.sendMessage(
                    chat_ID, "Here the devices, select one:", reply_markup=keyboard
                )


if __name__ == "__main__":
    TOKEN = "<your_token>"
