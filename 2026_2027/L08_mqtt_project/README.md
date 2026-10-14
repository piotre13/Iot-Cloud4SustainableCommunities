# L08 - MQTT in the project

## Goals
- Put MQTT inside the real project: the device connector publishes and listens, a controller reacts.
- Use topic wildcards so ONE controller serves every house and every room.
- See a new room appear at runtime without restarting anything.

## Architecture
The **catalog** (REST) is used for *discovery*: where is the broker, which are the thresholds of a room,
which devices exist. The **data** (measurements, commands, alerts) travels over **MQTT**.

```
 device_connector --REST POST /devices--> catalog <--GET /broker, /thresholds-- controller
        |  pub smarthome/<house>/<room>/temperature|humidity (SenML)                 ^
        |  pub smarthome/<house>/<room>/hvac/state                                   |
        +---------------------------- mosquitto ------------------------------------+
        ^  sub smarthome/<house>/<room>/hvac  {"command": "ON"}   (controller publishes it)
```

Topics (same as the final project):

| Topic | Payload |
|---|---|
| `smarthome/{house}/{room}/temperature`, `.../humidity` | SenML `{"bn","bt","e":[{"n","u","t","v"}]}` |
| `smarthome/{house}/{room}/hvac` | `{"command": "ON"}` or `{"command": "OFF"}` |
| `smarthome/{house}/{room}/hvac/state` | `{"state": "ON"}` |
| `smarthome/{house}/alerts` | `{"room": "kitchen", "msg": "..."}` |

Controller rules: temperature below `t_min` -> HVAC ON; above `t_max` -> HVAC OFF; humidity above `h_max` -> alert.
Commands and alerts are sent **only when the situation changes** (not at every measurement), and the
thresholds are read from the catalog **at every message**, so a change is used immediately.
The controller also listens to `hvac/state`, so it knows the real state (e.g. after a manual REST command).

The complete project (ThingSpeak adaptor, Telegram bot, launcher) is in `smart_home/`; we add those in later lessons.

## Files
`solution/` and `starter/` are flat folders: all modules side by side, run from inside the folder.
`catalog.py` (+ `catalog.json`), `mymqtt.py`, `senml.py`, `config.py` (+ `settings.json`), `devices.py`
are complete. You write the new parts of `device_connector.py` (Ex1) and `controller.py` (Ex2).

## How to run (one terminal each, from `solution/` or your finished `starter/`)
Install the requirements once: `pip install -r ../../requirements.txt` (or use the course venv).

1. Broker: `mosquitto` (default port 1883)
2. Catalog: `python catalog.py` (port 8080)
3. Controller: `python controller.py`
4. Connectors:
   - `python device_connector.py house1 kitchen 8081`
   - `python device_connector.py house1 bedroom 8082`
   - `python device_connector.py house2 bedroom 8083 --interval 5`

Options: `--source random|csv` (csv replays `../../data/meteo_frassinetto.csv`), `--interval SECONDS`, `--catalog URL`.

**Watch everything** in one more terminal: `mosquitto_sub -t 'smarthome/#' -v`

Note: in the starter, the connector stays alive after the TODO error (the web server thread keeps running): press Ctrl+C.

Automatic check of the whole solution (teacher tool, own broker on port 1886): `python test_e2e.py` in `solution/`
(needs `/opt/homebrew/sbin/mosquitto`; edit the path if your mosquitto lives elsewhere).

## Exercises

### Ex1 - Device connector v3 (`device_connector.py`)
Add MQTT to the connector from L05. Complete the TODOs:
1. `publish_measurements`: publish every SenML record on `smarthome/<house>/<room>/<sensor>`.
2. `actuate`: after the HVAC changes, publish `{"state": ...}` on `.../hvac/state`.
3. `notify`: receives the messages on `.../hvac`; apply `payload["command"]` and ignore bad payloads.
4. `main`: ask the catalog for the broker, create and start `MyMQTT`, subscribe to the hvac topic,
   and register the device in the catalog (`POST /devices`) so the catalog knows the room.

### Ex2 - Controller as a service (`controller.py`)
Complete `notify`, `check_temperature`, `check_humidity`:
- one process for all houses: subscriptions with wildcards `smarthome/+/+/temperature`,
  `smarthome/+/+/humidity`, `smarthome/+/+/hvac/state` (already in `main`: understand what `+` matches);
- get the thresholds with `GET /houses/<house>/<room>/thresholds`;
- ON/OFF commands and humidity alerts **only on change**.

### Ex3 - Add a room at runtime, change a threshold
With everything running (kitchen, bedroom, controller), do NOT restart anything:
1. Launch one more connector: `python device_connector.py house1 garage 8084`.
   Check `curl localhost:8080/houses/house1/garage/thresholds`: the catalog created the room with the default thresholds.
   Watch the controller handle it with `mosquitto_sub -t 'smarthome/#' -v`.
2. Change a threshold:
   `curl -X PUT localhost:8080/houses/house1/garage/thresholds -H 'Content-Type: application/json' -d '{"t_min": 25}'`
   and see how the commands change from the next measurement.
3. Force a value by hand: `mosquitto_pub -t smarthome/house1/garage/temperature -m '{"bn": "house1/garage", "bt": 0, "e": [{"n": "temperature", "u": "Cel", "t": 0, "v": 10}]}'` and see the HVAC turn ON.
