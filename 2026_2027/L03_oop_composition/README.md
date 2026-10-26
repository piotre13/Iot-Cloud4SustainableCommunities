# L03 - OOP 2: composition (1.5 h)

## Goals
- Tell apart **inheritance ("is-a")** from **composition ("has-a")**.
- Make objects collaborate: a connector uses sensors and an HVAC, a controller decides, `main` connects them.
- Load the rooms from a config file instead of writing them in the code.

## Theory in 5 minutes
- **Inheritance, is-a**: `TemperatureSensor` is a `Sensor` (last lesson, `devices.py`).
- **Composition, has-a**: a `DeviceConnector` has sensors and has an HVAC. We pass them to the constructor and keep them as attributes. The connector does not care which kind of sensor it gets (random, CSV, ...): it only calls `sense()`.
- **Separation of duties**: the connector reads and acts, the controller decides. Neither knows the other; `main` passes the data between them. This is what lets us replace the pieces later (MQTT in L07, thresholds from the catalog in L07).
- **Config instead of code**: `config.json` lists houses, rooms and thresholds. **Adding a room = editing `config.json`, no code change.** (Exam requirement.)

## Files
| File | What | Status |
|---|---|---|
| `devices.py` | sensors + HVAC | complete, last lesson's result |
| `device_connector.py` | `DeviceConnector`, v1 | Ex5 |
| `controller.py` | `Controller`, v1 | Ex6 |
| `main.py` | builds rooms from `config.json`, loops | Ex7 |
| `config.json` | houses, rooms, thresholds | given |

## Exercises
**Ex5 - `device_connector.py`**
`DeviceConnector(house_id, room_id, sensors, hvac)` holds its sensors and its HVAC.
- `read_sensors()` returns a dict like `{"temperature": 21.4, "humidity": 55.0}` and stores it in `self.latest`.
- `actuate(command)` forwards the command to the HVAC.
- `status()` returns a readable dict: house, room, latest measurements, HVAC state.
- No control logic here.

**Ex6 - `controller.py`**
`Controller(thresholds)`, with `decide(measurements)` returning `(command, alert)`:
- `temperature < t_min` -> `"ON"`; `temperature > t_max` -> `"OFF"`; inside the band -> `None` (leave as is).
- `humidity > h_max` -> alert string such as `humidity 78% > 70%`, otherwise `None`.

**Ex7 - `main.py`**
Complete `build_rooms()`: read `config.json`, and for every room build one `DeviceConnector` (random sensors + `HVAC()`) and one `Controller`.
The loop is given: every cycle, read, decide, and call `actuate` **only if the command differs from the current HVAC state**. Print measurements, commands and alerts.
Then add a room to `config.json` and run again, without touching the code.

## How to run
```
cd solution        # or starter
python main.py     # 3 cycles
python main.py 5   # 5 cycles, 1 s sleep between cycles
```
Needs `pandas` (imported by `devices.py` for `CsvSensor`). The starter fails with `NotImplementedError("TODO ...")` until the exercises are done.
