# L12 - Integration (3 h)

Goal: run the whole smart home (`smart_home/`), understand how the services fit together, extend it at runtime
without touching code, and map the exam-project requirements onto this reference code.

This lesson has no copy of the project: the solution **is** `smart_home/`. Here you only find this README and small scripts.

## 1. Architecture

```
                     REST (discovery, configuration)
        +---------------------------------------------------+
        |                  CATALOG  :8080                   |
        |  broker, houses/rooms/thresholds, devices, users, |
        |  ThingSpeak field map                             |
        +---------------------------------------------------+
          ^ POST /devices   ^ GET thresholds   ^ GET /thingspeak   ^ GET/PUT/POST (houses, users, thresholds)
          |                 |                  |                   |
 +--------+-------+   +-----+------+   +-------+--------+   +------+-------+
 | device         |   | controller |   | thingspeak     |   | telegram     |
 | connector x N  |   |            |   | adaptor        |   | bot          |
 | (1 per room)   |   |            |   |                |   |              |
 +---+--------^---+   +--+------^--+   +-------+--------+   +------+---^---+
     |        |          |      |              |                   |   |
     | MQTT   | MQTT     | MQTT | MQTT         | MQTT (sub)        |   | Telegram API (REST)
     v        |          v      |              v                   v   |
 +-------------------------------------------------------------------------+
 |                       MQTT BROKER (mosquitto :1883)                     |
 +-------------------------------------------------------------------------+
                                                |
                                                v  HTTPS GET /update
                                         ThingSpeak (external REST service)
```

- **REST** for "who/where/what are the settings" (catalog is the only source of truth, found at the URL in `smart_home/config/settings.json`).
- **MQTT** for the data flow (measurements, commands, states, alerts).
- **ThingSpeak** and **Telegram** are external REST services, reached only through their own adaptor service.
- Every service asks the catalog where the broker is. Nobody hard-codes anything except the catalog URL.

### MQTT topics

| Topic | Published by | Subscribed by | Payload |
|---|---|---|---|
| `smarthome/{house}/{room}/temperature` | device connector | controller, adaptor, bot | SenML `{"bn","bt","e":[{"n","u","t","v"}]}` |
| `smarthome/{house}/{room}/humidity` | device connector | controller, adaptor, bot | SenML |
| `smarthome/{house}/{room}/hvac` | controller | device connector of that room | `{"command": "ON"\|"OFF"}` |
| `smarthome/{house}/{room}/hvac/state` | device connector | controller, adaptor, bot | `{"state": "ON"\|"OFF"}` |
| `smarthome/{house}/alerts` | controller | bot | `{"room": ..., "msg": ...}` |

### Catalog endpoints (`smart_home/catalog/service.py`)

| Method | Path | Meaning |
|---|---|---|
| GET | `/broker` | broker host and port |
| GET | `/houses` | all houses with rooms and thresholds |
| POST | `/houses` | create/replace a house (upsert by `house_id`) |
| GET | `/houses/<house_id>` | one house |
| GET | `/houses/<house_id>/<room_id>/thresholds` | `t_min`, `t_max`, `h_max` of a room |
| PUT | `/houses/<house_id>/<room_id>/thresholds` | change any of `t_min`, `t_max`, `h_max` |
| GET | `/devices`, `/devices/<device_id>` | registered device connectors |
| POST | `/devices` | register a device (upsert by `device_id`); creates house and room if missing |
| GET | `/users` | Telegram users |
| POST | `/users` | register a user (upsert by `chat_id`) |
| GET | `/thingspeak` | channel id and `topic -> field` map |
| PUT | `/thingspeak` | replace that map |

## 2. How to run

All commands from `2026_2027/` with the course virtual environment active.

1. Broker (own terminal): `/opt/homebrew/sbin/mosquitto` (it is not in the PATH on Homebrew/Apple Silicon).
2. Secrets (optional): copy `.env.example` to `2026_2027/.env` and fill `TELEGRAM_TOKEN` and `THINGSPEAK_WRITE_KEY`.
   Without the ThingSpeak key the adaptor runs in **dry run** (it prints the updates); without the Telegram token the bot is **skipped**.
   Never commit `.env`.
3. Everything at once:
   ```
   cd smart_home
   python launch_all.py
   ```
   It starts catalog, controller, ThingSpeak adaptor, (bot) and one connector for each of the 4 rooms (house1: kitchen, bedroom; house2: living_room, bedroom).
   **Ctrl+C** stops all of them.
4. Logs: `smart_home/logs/<service>.log`, e.g. `tail -f smart_home/logs/controller.log`.
5. Watch the traffic: `mosquitto_sub -t 'smarthome/#' -v`
   (the adaptor sends to ThingSpeak at most every 15 s, so wait a bit for its log lines.)
6. Tests, from `smart_home/` (they start their own mosquitto on a test port; set `MOSQUITTO=/path/to/mosquitto` if it is not at `/opt/homebrew/sbin`):
   ```
   python -m tests.test_catalog
   python -m tests.test_common
   python -m tests.test_e2e
   python -m tests.test_s3_dry_run
   ```

## 3. Exercises

### Ex1 - Follow one measurement end to end
Run the system (2 houses x 2 rooms) and follow one temperature reading through all the services:

1. `mosquitto_sub -t 'smarthome/house1/kitchen/#' -v`: see the SenML measurement published by the connector.
2. `logs/dc_house1_kitchen.log`: the same value printed by the connector.
3. `logs/controller.log`: the controller read the thresholds from the catalog and (if the value crossed one) sent `hvac ON/OFF`.
4. The connector executes the command and publishes `.../hvac/state`: find it in the `mosquitto_sub` window.
5. `logs/thingspeak_adaptor.log`: the `[dry run] GET .../update {'field1': ...}` line containing that value (`field3` is the HVAC of house1/kitchen, 1 = ON).
6. `curl http://localhost:8081/` asks the connector's REST API for its latest measurements and HVAC state.

Question: which of these steps use REST and which use MQTT? Why?

### Ex2 - Add a whole house at runtime
Without touching any code or restarting anything, add `house3` with two rooms to the running system:

```
cd L12_integration/solution      # (or starter, once completed)
python add_house.py house3 kitchen bedroom --first-port 8085
```
(this is the same as launching `python -m device_connector.service house3 kitchen 8085` and `... house3 bedroom 8086` by hand from `smart_home/`).
Check:
- `curl http://localhost:8080/houses` and `/devices`: the house, the rooms (with default thresholds) and the devices exist.
- `logs/controller.log` shows lines for `house3/...`: the wildcard subscriptions and the catalog made it work with no change.
- The bot lists `house3` in `/start` (if you have a token).
- `logs/thingspeak_adaptor.log` shows nothing for house3: the catalog has no ThingSpeak fields for it. Add them with `PUT /thingspeak` (a free channel has only 8 fields).

Ctrl+C in the `add_house.py` terminal stops the new connectors.

### Ex3 - Change thresholds from the catalog
```
cd L12_integration/solution
python change_threshold.py house1 kitchen t_min 21.5
```
or with curl:
```
curl -X PUT -H "Content-Type: application/json" -d '{"t_min": 21.5}' http://localhost:8080/houses/house1/kitchen/thresholds
```
Watch `logs/controller.log`: from the next measurement the controller uses the new limit (it reads the catalog at every message). Try an invalid value (`t_min` higher than `t_max`, an unknown room): which HTTP error do you get?

### Extra - Your own exercises
- Run a connector with `--source csv --interval 2` for a new room and watch the data come from the weather file.
- Stop the controller only (find its pid): what keeps working, what stops? Restart it: does it recover?
- Stop the catalog while everything runs. Which services fail, which keep going? (Hint: who calls the catalog at each message?)

### Ex4 (discussion) - Exam project checklist

| Requirement | Where in `smart_home/` |
|---|---|
| Microservices: one process per service | `catalog/`, `controller/`, `device_connector/`, `thingspeak_adaptor/`, `telegram_bot/`, each with its own `service.py`, started by `launch_all.py` as separate processes |
| OOP | `DeviceConnector`, `Controller`, `ThingSpeakAdaptor`, `SmartHomeBot`, `CatalogStore`/`CatalogAPI`; `Sensor` -> `RandomSensor`/`CsvSensor` and `HVAC` in `device_connector/devices.py`; `MyMQTT` in `common/` |
| JSON configuration | `config/settings.json` (catalog URL), `catalog/catalog.json` (seed: broker, houses, thresholds, ThingSpeak map) |
| Only REST and MQTT between services | REST: catalog and connector API; MQTT: all measurements, commands, alerts; no shared files or imports between services |
| Service discovery | everybody asks the catalog for the broker (`common/config.py: get_broker`); the connector registers itself with `POST /devices` |
| Runtime add of devices, users, houses | `POST /devices` creates house and room; `POST /users` from the bot's `/start`; Ex2 |
| Configuration changed at runtime | thresholds via `PUT .../thresholds` (Ex3), read at each message by the controller |
| Proper data format | SenML records in `common/senml.py` (`bn`, `bt`, and the list `e` with `n`, `u`, `t`, `v`) |
| External services | ThingSpeak (REST, behind `thingspeak_adaptor/`), Telegram (`telegram_bot/`) |
| Secrets out of the code | `get_secret()` reads `2026_2027/.env`; `.env` is git-ignored |
| Tests | `tests/` (catalog, common/MQTT, end to end, adaptor dry run) |
| One command to start | `launch_all.py` (+ logs per service) |

#### Recommended structure for your exam project
```
my_project/
  README.md            what it is, architecture, how to run, how to test
  requirements.txt
  .env.example         names of the secrets, no values; .env itself is git-ignored
  .gitignore           .env, logs/, runtime state files
  launch_all.py        starts every service as a separate process, Ctrl+C stops all
  config/settings.json catalog URL and other settings
  common/              code shared by services (MQTT wrapper, config, data format)
  catalog/service.py   one folder per service, each with its own service.py
  <service_a>/service.py
  <service_b>/service.py
  tests/
```

#### Common mistakes
- Hard-coded IPs, ports, topics or tokens spread in the code: put them in config or ask the catalog.
- A monolith: everything in one script/process, or services that import each other instead of talking over REST/MQTT.
- Secrets (bot token, API keys) committed to git. If it happens, revoke the key: deleting the commit is not enough.
- No runtime registration: devices, users or houses that can be added only by editing a file and restarting.
- Not reading the thresholds/configuration again from the catalog, so changes need a restart.
- Non-standard data formats, or no way to tell what unit a value has.
- No README, no way to start the whole system with one command, no tests.
- Services that crash on the first bad message (wrap the message handler in try/except).

## 4. Files

- `solution/add_house.py`, `solution/change_threshold.py`: complete scripts (Ex2, Ex3).
- `starter/add_house.py`, `starter/change_threshold.py`: same files with the `raise NotImplementedError("TODO ExN: ...")` parts to write.
