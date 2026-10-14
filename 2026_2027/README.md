# Programming for IoT — course material 2026/27

One project, built lesson by lesson: a **smart home** with temperature/humidity sensors and an ON/OFF HVAC (heater)
in every room, scalable to many houses. Every lesson adds a module that stays in the final project, following the
exam rules: microservices, object-oriented code, JSON configuration, communication only over REST and MQTT,
devices and houses added at runtime without changing the code.

```
                  Catalog (REST, CherryPy + JSON file)
        houses · rooms · thresholds · devices · users · broker address
          ▲ register        ▲ thresholds      ▲ field map       ▲ thresholds, users
          │                 │                 │                 │
   Device Connector     Controller     ThingSpeak Adaptor    Telegram Bot
   (1 per room)       (1 for all houses)  (→ ThingSpeak REST)  (→ Telegram API)
   pub T/H, state       sub T/H            sub T/H, state       sub alerts
   sub HVAC command     pub command, alerts
          │                 │                 │                 │
          └──────────── MQTT broker (mosquitto, local) ─────────┘
```

## Setup

```bash
cd 2026_2027
python3.12 -m venv .venv
source .venv/bin/activate          # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # put your own keys here; .env is never committed
```
You also need a local MQTT broker: [mosquitto](https://mosquitto.org/download/) (`brew install mosquitto` on macOS,
then run `mosquitto -v`; on Apple Silicon the binary is in `/opt/homebrew/sbin`).

## Lessons

Each lesson folder has a `README.md` (goals, short theory, exercises, how to run), a `starter/` (skeletons: every
TODO raises `NotImplementedError`) and a `solution/` (complete, run it from inside its folder).

| Lesson | Topic | Module added to the project |
| --- | --- | --- |
| [L01](L01_intro/) | Intro, environment, Python refresh | `config.json`, setup |
| [L02](L02_oop_basics/) | OOP 1: classes, inheritance, polymorphism | `devices.py` (sensors, HVAC) |
| [L03](L03_oop_composition/) | OOP 2: composition | `device_connector.py` v1, `controller.py` v1 |
| [L04](L04_rest_basics/) | REST client + CherryPy basics, project proposal | CherryPy base |
| [L05](L05_rest_device/) | REST server for the device | `device_connector.py` v2 (REST) |
| [L06](L06_catalog/) | Catalog | `catalog.py` + registration at start-up |
| [L07](L07_mqtt_basics/) | MQTT basics, SenML | `mymqtt.py`, `senml.py` |
| [L08](L08_mqtt_project/) | MQTT in the project | `device_connector.py` v3 (MQTT), controller service |
| [L09](L09_thingspeak/) | ThingSpeak, third-party REST API | `thingspeak_adaptor.py` |
| [L10](L10_telegram_basics/) | Telegram bots basics (telebot; telepot as reference) | `bot_basics.py` |
| [L11](L11_telegram_project/) | Telegram bot in the project | `telegram_bot.py` |
| [L12](L12_integration/) | Integration of the whole system | `smart_home/` complete |
| [L13](L13_revision/) | Revision and exam practice | `exam_practice/` |

## The complete project: `smart_home/`

```bash
cd smart_home
python launch_all.py               # catalog, controller, ThingSpeak adaptor, Telegram bot (if token), 4 rooms
```
Logs go to `smart_home/logs/<service>.log`; watch the messages with `mosquitto_sub -t 'smarthome/#' -v`.
Without keys in `.env` the ThingSpeak adaptor runs in dry run (prints the updates) and the bot is not started.
Tests (from `smart_home/`, mosquitto needed): `python -m tests.test_catalog`, `tests.test_common`, `tests.test_e2e`,
`tests.test_s3_dry_run`.

## Conventions

| Use | MQTT topic | Payload |
| --- | --- | --- |
| Measurements | `smarthome/{house}/{room}/temperature` (and `/humidity`) | SenML `{"bn": "house1/kitchen", "bt": 1791970000, "e": [{"n": "temperature", "u": "Cel", "t": 0, "v": 21.4}]}` |
| HVAC command | `smarthome/{house}/{room}/hvac` | `{"command": "ON"}` |
| HVAC state | `smarthome/{house}/{room}/hvac/state` | `{"state": "ON"}` |
| Alerts | `smarthome/{house}/alerts` | `{"room": "kitchen", "msg": "humidity 78% > 70%"}` |

Catalog endpoints: `GET /broker` · `GET|POST /houses` · `GET /houses/<house>` · `GET|PUT /houses/<house>/<room>/thresholds`
· `GET|POST /devices` · `GET /devices/<id>` · `GET|POST /users` · `GET|PUT /thingspeak`.

## Secrets

Tokens and API keys live only in `2026_2027/.env` (see `.env.example`). Never commit them, never paste them in code.
If a key ends up in a commit, revoke it (BotFather `/revoke`, ThingSpeak "Generate New Write API Key").

The 2025/26 material in `../2025_2026/` is kept unchanged as an archive.
