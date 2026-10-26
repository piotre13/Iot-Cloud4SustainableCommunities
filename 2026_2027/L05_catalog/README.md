# L05 - The Catalog (3 h)

## Goals
- Understand why an IoT system needs a catalog (service discovery) and design its REST resources.
- Build the Catalog service with CherryPy and a JSON file as storage.
- Make a device connector register itself, so a brand new room appears in the system at runtime without touching any code.
- Write a small client that talks to the catalog.

## Theory in short
- **Why a catalog.** Services must not hard-code addresses, broker, thresholds or the list of rooms. They ask the catalog: "where is the broker?", "which rooms exist?", "which thresholds for house1/kitchen?". This is *service discovery*: add a room or change a threshold by changing the catalog, not the code.
- **Resource design.** Nouns in the URL, verbs are HTTP methods: `GET /houses`, `GET /houses/house1`, `GET /houses/house1/kitchen/thresholds`, `PUT` on the same URL to change them. A hierarchy in the data = a hierarchy in the URL.
- **Upsert.** `POST /devices` with an existing `device_id` replaces that device, with a new one adds it. Calling it twice gives the same result (idempotent), so a connector can register at every start without checking first. The same for `/houses` (key `house_id`) and `/users` (key `chat_id`). Registering a device also creates its house and room, with `default_thresholds`.
- **Persistence.** `catalog.json` is the *seed*: it is never modified. At first start it is copied to `catalog_state.json`, and the running service reads/writes only the copy. Why: the seed in git stays clean (a test run does not leave your experiments in it), and "reset the system" = delete the state file. The save writes a temporary file and then `os.replace` (atomic): a crash never leaves a half-written JSON.
- **Thread safety.** CherryPy handles each request in a different thread. Two simultaneous POSTs could modify the same list and write the file at the same time. A single `RLock` around every read-modify-save sequence makes requests go one at a time on the data.
- **Status codes.** 200 OK (GET/PUT), 201 Created (POST), 400 bad body (invalid JSON, missing key, not a number, `t_min >= t_max`), 404 unknown house/room/device/endpoint.

## Files
| file | what |
|---|---|
| `catalog.json` | seed with broker, default_thresholds, houses, devices, users, thingspeak |
| `catalog.py` | the service (Ex1, Ex2) |
| `devices.py` | sensors and HVAC (as in L03, given) |
| `device_connector.py` | connector of one room (as L03: sensors + HVAC) + registration (Ex3) |
| `catalog_client.py` | client script (Ex4) |
| `extra_heartbeat/` | optional extra (see the end) |

In `starter/` the store, the helpers (`read_json_body`, `require`, `upsert`) and the rest of the connector are complete: only the `TODO` parts are missing.

## Exercises

### Ex1 - GET of the catalog (`catalog.py`)
Implement `CatalogAPI.GET` (inside `with self.store.lock:`):
`/broker`, `/houses`, `/houses/<house_id>`, `/houses/<house_id>/<room_id>/thresholds`, `/devices`, `/devices/<device_id>`, `/users`, `/thingspeak`.
A missing house, room or device gives **404**, an unknown URL gives 404. Use `self.store.find_house` / `find_room`.

### Ex2 - POST and PUT (`catalog.py`)
- `POST /houses` (keys `house_id`, `rooms`), `POST /devices` (keys `device_id`, `house_id`, `room_id`, `sensors`), `POST /users` (keys `chat_id`, `name`, `houses`): `require(...)` the keys (400), `upsert(...)`, for devices also `ensure_room(...)`, then `save()` and answer **201** with the object. For `POST /devices` the answer is the *configuration of the device*: `{"device": <the object>, "broker": {host, port}, "base_topic": "smarthome/<house>/<room>", "interval": <seconds>}` (given as `self.device_config(obj)`; `default_interval` is in the seed). The device needs nothing else to start.
- `PUT /houses/<h>/<r>/thresholds`: room not found = 404; body must be a non-empty object with only `t_min`, `t_max`, `h_max` and finite numbers, else 400; **partial update** (keys not sent stay as they are); after the update `t_min` must be lower than `t_max`, else 400 and nothing changes.
- `PUT /thingspeak`: keys `channel_id`, `fields`; replaces the section.
- Always `save()` after a change, inside the lock.

### Ex3 - Self-registering device connector (`device_connector.py`)
**Registering is the first thing a device does**: "I am here". In `main` the connector calls `dc.register(catalog)` before anything else: `POST {catalog}/devices` with
`{"device_id": "dc_<house>_<room>", "house_id", "room_id", "sensors": ["temperature","humidity"]}` (method `DeviceConnector.register`). The catalog stores it and **answers with all the configuration the device needs** (broker, base topic, publish interval): `register` returns it, `main` prints it and uses `interval` (the `--interval` option overrides it). From L07 the broker of that answer is used to start MQTT: the only thing hard-coded in a device is the URL of the catalog. Show that **a brand new room appears in the catalog at runtime**: start `house1 garage` and read `GET /houses/house1`: the room `garage` is there, with the default thresholds, and no line of code was changed.

### Ex4 - Catalog client (`catalog_client.py`)
With `requests`: list the houses and their rooms; read the thresholds of `house1/kitchen`; change `t_max` with a partial PUT; try an invalid PUT (`t_min` = 40) and print the 400; list the registered devices.

## How to run
All commands from inside `solution/` (or `starter/`), using the course virtual environment. Open one terminal per line, **in this order**:

```
1) python catalog.py                                   # port 8080, state in catalog_state.json
2) python device_connector.py house1 garage            # registers itself in the catalog
3) python catalog_client.py
```
Options: `python catalog.py 8120 my_state.json` (port, state file), `python device_connector.py house1 garage --catalog http://localhost:8120`, `python catalog_client.py http://localhost:8120`.

### curl examples
The header `Content-Type: application/json` is required on POST/PUT with curl: without it curl sends the body as a web form and CherryPy answers 400 "Unexpected body parameters". (`requests` with `json=` sets it for you.)
```
curl localhost:8080/broker
curl localhost:8080/houses
curl localhost:8080/houses/house1/kitchen/thresholds
curl -X PUT -H "Content-Type: application/json" -d '{"t_max": 25}' localhost:8080/houses/house1/kitchen/thresholds
curl -X PUT -H "Content-Type: application/json" -d '{"t_min": 40}' localhost:8080/houses/house1/kitchen/thresholds     # 400
curl -X POST -H "Content-Type: application/json" -d '{"device_id":"dc_house1_attic","house_id":"house1","room_id":"attic","sensors":["temperature"]}' localhost:8080/devices
curl localhost:8080/devices/dc_house1_attic
curl -X POST -H "Content-Type: application/json" -d '{"chat_id":1,"name":"Anna","houses":["house1"]}' localhost:8080/users
curl localhost:8080/houses/house9                                                                                      # 404
```
To start again from the seed: stop the catalog and delete `catalog_state.json`.

## EXTRA (optional) - heartbeat (`extra_heartbeat/`)
Self-contained copy of the files. The connector re-POSTs its registration every 60 s with `"last_seen": <unix time>` (upsert, so it just updates the entry); the catalog removes the devices not seen for more than 120 s. We chose the simplest option: the check runs at each `GET /devices...` (no background thread). Devices without `last_seen` (e.g. in the seed) are never removed. Run from inside `extra_heartbeat/`, same commands as above.
**The main project (`smart_home`) does NOT use the heartbeat**: devices register once at start-up and stay in the catalog.
