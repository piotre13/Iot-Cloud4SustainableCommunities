# L10 - Telegram bots, basics (1.5 h)

## Goals
- Create a Telegram bot with @BotFather and keep its token secret.
- Write a bot with `pyTelegramBotAPI` (`telebot`): commands, echo, inline keyboard with buttons.
- Know the old library `telepot`, because you will find it in old code.

## Theory
**A bot** is a normal Telegram account run by a program. Users write to it; Telegram sends our program an *update*
(a message, a button press...) and our program answers with `send_message`, ...

**@BotFather** (the official bot that creates bots):
1. In Telegram search `@BotFather`, send `/newbot`.
2. Choose a display name and a username (must end with `bot`).
3. BotFather answers with the **token** (`123456:ABC...`).
4. Optional: `/setcommands` to get the command menu.

**The token is a secret**: whoever has it controls your bot. Never write it in the code, never commit it.
Copy `2026_2027/.env.example` to `2026_2027/.env` (ignored by git) and write `TELEGRAM_TOKEN=...`; the code reads it with `python-dotenv`.
If a token leaks: `/revoke` in BotFather.

**Polling vs webhook**: with *polling* our program keeps asking Telegram "any news?" (works behind any router, we use this);
with a *webhook* Telegram calls a public URL of ours (needs a server with HTTPS).

**Handlers**: we tell the bot which function handles which update: `register_message_handler(function, commands=["start"])`
for a command, `content_types=["text"]` for any text, `register_callback_query_handler` for button presses.
The first matching handler wins, so the generic text handler is registered after the commands.

**Inline keyboard**: buttons attached to a message. Each button has a text and a `callback_data` string; pressing it sends us a
*callback query* with that string (max **64 bytes**), e.g. `"hvac:ON"`. We must call `answer_callback_query(call.id)`, otherwise
the button keeps showing a loading spinner. Convention of our project: `action:arg1:arg2`, split with `split(":")`.

## telebot vs telepot
| | telebot (pyTelegramBotAPI) | telepot |
|---|---|---|
| Maintained? | yes, active | no, last release 2019 |
| Sync / async | sync (async version `AsyncTeleBot` exists) | sync (threads) |
| Handlers | one registration per command / content type | one function per message *flavor* (`chat`, `callback_query`), `if` on the text |
| Message data | objects: `message.chat.id`, `message.text` | raw dicts + `telepot.glance(msg)` |
| Keyboards | `types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(...))` | `InlineKeyboardMarkup(inline_keyboard=[[...]])` from `telepot.namedtuple` |
| Start | `bot.infinity_polling()` | `MessageLoop(bot, handlers).run_as_thread()` |

## Files
`bot_basics.py` (the exercises), `telepot_reference.py` (the same bot in telepot, comparison only, do not run),
`check_bot.py` (solution only: offline test, no token needed).
Work in `starter/`, compare with `solution/`. Run everything from inside the folder.

## Exercises
### Ex1 - `bot_basics.py`: commands and echo
The code loads the token (`get_secret`) and stops with a clear message if `.env` is missing. Class `EchoBot(bot)` registers its handlers.
Write `on_start` (welcome with the user's first name), `on_help` (list of commands) and `on_text` (repeat any other text).

### Ex2 - inline keyboard
- `/hvac` shows a message with two buttons **ON** and **OFF** (`callback_data` `hvac:ON` / `hvac:OFF`).
- `on_button` answers the callback query and replies `HVAC switched ON (simulated)`.
- `/temp` replies with a random temperature (no connection to the project yet: in L11 the bot talks to the catalog).

### Reference - `telepot_reference.py`
Read it next to `bot_basics.py` and find, line by line, what changes. Do not run it.

## How to run
    # once: create the bot with @BotFather, copy ../.env.example to ../.env and put the token in it
    cd starter        # or solution
    python bot_basics.py
Then in Telegram open your bot and try `/start`, `/help`, `/hvac`, `/temp`, a normal text.
Without `.env` the program exits and tells you how to create it.

Teacher / no token: `cd solution && python check_bot.py` runs the same handlers with a fake bot and fake updates.
