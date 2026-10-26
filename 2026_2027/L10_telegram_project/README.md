# L10 - The Telegram bot in the project (3 h)

## Goals
- Build the last service of the smart home: a Telegram bot for the users.
- See a bot as a microservice: a REST client of the catalog, plus an MQTT subscriber.
- Keep per-chat state (the bot waits for a number) and send alerts to the right people.

## Theory
**The bot is not special.** Like the controller, it only talks to the other services:
- *REST client*: users, houses, thresholds from the **catalog**.
- *MQTT subscriber*: `smarthome/+/alerts` (published by the controller) and the measurements and `hvac/state` of every room. `MyMQTT` calls `notify(topic, payload)` of the bot, which forwards the alerts and **remembers the last value of every room** in `self.latest`.
- Why not ask the device? Devices have no REST server: they publish. The bot is a subscriber like the controller. `hvac/state` is *retained*, so right after a restart the bot already knows the HVAC state; measurements arrive at the next publish (a few seconds): until then the room view says "no data yet". The age of the value comes from the SenML `bt`.
- Telegram is only the user interface. Library: `pyTelegramBotAPI` (`import telebot`). `infinity_polling()` asks Telegram for new messages and calls our handlers.

**Inline keyboard**: buttons under a message. Pressing a button sends a `callback_data` string to the bot (here `follow:house1`, `house:house1`, `room:house1:kitchen`, `set:house1:kitchen:t_min`). One handler (`on_button`) splits it with `split(":")` and decides what to do.

**Waiting state**: Telegram has no "conversation". After the button `set:...` the bot stores `waiting_value[chat_id] = (house, room, key)`; the next plain text of that chat is the new value. Without waiting state, text gets the help message.

Flow:

    /start -> buttons follow:<house> -> POST /users (chat_id, name, houses)
    /houses -> buttons house:<h> -> buttons room:<h>:<r> -> room view
         (GET catalog thresholds + latest measurements/HVAC remembered from MQTT)
    room view -> button set:<h>:<r>:<key> -> waiting_value[chat]
         -> user types "21,5" -> PUT /houses/<h>/<r>/thresholds
            ok: confirmation     400: "Not accepted", still waiting
    controller -> MQTT smarthome/<h>/alerts -> notify -> send to every user following <h>
    device     -> MQTT smarthome/<h>/<r>/temperature|humidity|hvac/state -> notify -> self.latest[(h, r)]

**Known limits (discussion topics for the exam projects)**
- *No authorization*: anyone who finds the bot can `/start`, follow a house and change its thresholds. Ideas: a list of allowed `chat_id` in the catalog, a password/invite code, roles (viewer / admin).
- *`callback_data` is limited to 64 bytes*: long house/room names break the buttons. Ideas: short ids, or store a lookup table in the bot.
- The waiting state lives in memory: a bot restart forgets it.

## Files
`config.py` (catalog URL from `settings.json`, `get_broker`, `get_secret`), `mymqtt.py`, `settings.json`, `telegram_bot.py`, and in `solution/` only `check_bot.py` (offline test).
Work in `starter/`, compare with `solution/`. Everything is already in place except the bodies of the bot methods marked `TODO ExN`. Run from inside the folder.

## Exercises (all in `telegram_bot.py`)
### Ex1 - `/start` and follow
`on_start`: ask the catalog for the houses (`GET /houses`) and send them as buttons `follow:<house>`.
`follow`: find the user of this chat (`get_user`) or create `{"chat_id", "name", "houses": []}`, add the house if missing, `POST /users`, answer with the followed houses.

### Ex2 - `/houses`, rooms and room view
`on_houses`: buttons `house:<house>` for the houses of this user (no user or no house -> "send /start").
`show_rooms`: `GET /houses/<house>`, buttons `room:<house>:<room>`.
`show_room`: thresholds from the catalog; measurements and HVAC from `self.latest[(house, room)]` with the age of each value (`time.time() - record["bt"]`); if the room has no data yet, write "no data yet". Add the buttons `set:<house>:<room>:<key>` for `t_min`, `t_max`, `h_max`.

### Ex3 - Change a threshold
`on_text`: if the chat is not waiting, answer "Commands: /start, /houses". Otherwise convert the text to a number (accept the comma `20,5`), `PUT /houses/<house>/<room>/thresholds` with `{key: value}`. Not a number -> ask again. Catalog answers 400 (for example `t_min` above `t_max`) -> tell the user, keep waiting. Catalog down -> tell the user. Success -> forget the waiting state and confirm.

### Ex4 - MQTT: alerts and latest values
`notify(topic, payload)` routes by topic: `smarthome/<house>/alerts` -> `forward_alert`; `.../hvac/state` -> `self.latest[(house, room)]["hvac"]`; `.../temperature|humidity` -> `self.latest[(house, room)][<name>]` (the SenML record). `forward_alert`: send `ALERT <house>/<room>: <msg>` to the users (`GET /users`) who follow that house. If one send fails (user blocked the bot), print it and go on with the others.

## How to run
1. Create the bot with @BotFather (Telegram), copy the token into `2026_2027/.env`: `TELEGRAM_TOKEN=...` (never commit it).
2. The system of L07 must run: broker, catalog, controller and the device connectors (separate terminals as in L07), or `cd smart_home && python launch_all.py`.
3. `cd L10_telegram_project/starter` (or `solution`) and `python telegram_bot.py` (add `--catalog URL` if the catalog is not on port 8080).
4. In Telegram: `/start`, press a house, `/houses`, house, room, "change t_max", type a value. To see an alert, push humidity above `h_max` (change `h_max` to a low value).

## Test without Telegram (solution folder)
No token needed. Start a broker and a catalog, then:

    python check_bot.py --catalog http://localhost:8080

It drives the real bot with fake updates and checks Ex1-Ex4 (alerts also through the broker). The catalog must be fresh (no users, default thresholds).
