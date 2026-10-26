"""Offline test of EchoBot: real telebot.TeleBot with a fake token, no network.
Run:  python check_bot.py
Updates are fed by hand and send_message / answer_callback_query are replaced by recorders.
"""
import telebot

from bot_basics import EchoBot

CHAT = 1001


def message_update(text):
    msg = {"message_id": 1, "date": 0, "chat": {"id": CHAT, "type": "private"},
           "from": {"id": CHAT, "is_bot": False, "first_name": "Ada"}, "text": text}
    if text.startswith("/"):
        msg["entities"] = [{"type": "bot_command", "offset": 0, "length": len(text)}]
    return telebot.types.Update.de_json({"update_id": 1, "message": msg})


def button_update(data):
    msg = {"message_id": 1, "date": 0, "chat": {"id": CHAT, "type": "private"}, "text": "HVAC:"}
    return telebot.types.Update.de_json({"update_id": 1, "callback_query": {
        "id": "7", "from": {"id": CHAT, "is_bot": False, "first_name": "Ada"},
        "chat_instance": "x", "data": data, "message": msg}})


def main():
    bot = telebot.TeleBot("123456:fake-token-for-tests", threaded=False)
    sent, answered = [], []

    def send_message(chat_id, text, reply_markup=None, **kwargs):
        buttons = [b.callback_data for row in reply_markup.keyboard for b in row] if reply_markup else []
        sent.append((chat_id, text, buttons))

    bot.send_message = send_message
    bot.answer_callback_query = lambda query_id, *a, **k: answered.append(query_id)
    EchoBot(bot)

    def feed(update):
        bot.process_new_updates([update])
        return sent[-1]

    assert "Hello Ada" in feed(message_update("/start"))[1]
    assert "/hvac" in feed(message_update("/help"))[1]
    assert feed(message_update("good morning")) == (CHAT, "You said: good morning", [])
    assert feed(message_update("/hvac"))[2] == ["hvac:ON", "hvac:OFF"]
    assert feed(button_update("hvac:ON"))[1] == "HVAC switched ON (simulated)"
    assert answered == ["7"]
    assert feed(button_update("hvac:OFF"))[1] == "HVAC switched OFF (simulated)"
    text = feed(message_update("/temp"))[1]
    assert 18 <= float(text.split()[1]) <= 26, text
    assert len("hvac:OFF".encode()) <= 64  # callback_data limit
    print("bot_basics: all checks passed")


if __name__ == "__main__":
    main()
