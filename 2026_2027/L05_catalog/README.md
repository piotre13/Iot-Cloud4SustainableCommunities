# L05 - The Catalog (3 h)

## Goals
- Understand why an IoT system needs a catalog (service discovery) and design its REST resources.
- Build the Catalog service with CherryPy and a JSON file as storage.
- Make a device connector register itself, so a brand new room appears in the system at runtime without touching any code.
- Write a small client that talks to the catalog.

## Theory in short
- **Why a catalog.** Services must not hard-code addresses, broker, thresholds or the list of rooms. They ask the catalog: "where is the broker?", "which rooms exist?", "which thresholds for house1/kitchen?". This is *service discovery*: add a room or change a threshold by changing the catalog, not the code.
- **Resource design.** Nouns in the URL, verbs are HTTP methods: `GET /houses`, `GET /houses/house1`, `GET /houses/house1/kitchen/thresholds`, `PUT` on the same URL to change them. A hierarchy in the data = a hierarchy in the URL.
- **Create vs update.** `POST` creates and never replaces: `POST /houses`, `POST /houses/<h>/rooms`, `POST /users` answer **409 Conflict** if the id already exists, so a stale or wrong request cannot silently overwrite data (a house replaced by a copy without rooms would lose all its thresholds). Updating is a `PUT` on the URL of the resource: `PUT /users/<chat_id>`, `PUT .../thresholds`. Rooms are a sub-resource of the house (`POST /houses/<h>/rooms`), so touching a house never touches its rooms.
- **Registration is a POST, and the device does it first.** A device is identified by *where it is and what it is*: house, room and type, the only things hard-coded in it, plus the names of the sensors and actuators it handles: `POST /devices` with `{"house_id": "house1", "room_id": "garage", "type": "device_connector", "sensors": ["temperature", "humidity"], "actuators": ["hvac"]}`. The catalog creates the device (and its house and room, with `default_thresholds`) and answers 201 with the configuration. **After a restart the same POST answers 409** (the device exists, nothing is replaced): the connector then reads the same answer with `GET /devices/house1/garage/device_connector`. Changing something of an existing device (e.g. it moved to another room) would be a `PUT` on that URL: not implemented yet.
- **Ids.** House, room and type are readable ids chosen by the client (they appear in MQTT topics); `chat_id` comes from Telegram. The catalog does not invent them but *guarantees they are unique* (409). The check "exists? then insert" is done under the lock, so two simultaneous requests cannot both create it.
- **Persistence.** `catalog.json` is the *seed*: it is never modified. At first start it is copied to `catalog_state.json`, and the running service reads/writes only the copy. Why: the seed in git stays clean (a test run does not leave your experiments in it), and "reset the system" = delete the state file. The save writes a temporary file and then `os.replace` (atomic): a crash never leaves a half-written JSON.
- **Thread safety.** CherryPy handles each request in a different thread. Two simultaneous requests could modify the same list and write the file at the same time. A single `RLock` around every read-modify-save sequence makes requests go one at a time on the data.
- **Status codes.** 200 OK (GET/PUT), 201 Created (POST), 400 bad body (invalid JSON, missing key, not a number, `t_min >= t_max`), 404 unknown house/room/device/user/endpoint, 409 the id already exists (POST).

## Files
| file | what |
|---|---|
| `catalog.json` | seed with broker, default_thresholds, houses, devices, users, thingspeak |
| `catalog.py` | the service (Ex1, Ex2) |
| `devices.py` | sensors and HVAC (as in L03, given) |
| `device_connector.py` | connector of one room (as L03: sensors + HVAC) + registration (Ex3) |
| `catalog_client.py` | client script (Ex4) |
In `starter/` the store, the helpers (`read_json_body`, `require`, `create`) and the rest of the connector are complete: only the `TODO` parts are missing.

## Exercises

### Ex1 - GET of the catalog (`catalog.py`)
Implement `CatalogAPI.GET` (inside `with self.store.lock:`):
`/broker`, `/houses`, `/houses/<house_id>`, `/houses/<house_id>/<room_id>/thresholds`, `/devices`, `/devices/<house_id>/<room_id>/<type>`, `/users`, `/thingspeak`.
A missing house, room or device gives **404**, an unknown URL gives 404. Use `self.store.find_house` / `find_room`.

### Ex2 - POST and PUT (`catalog.py`)
- `POST /houses` (key `house_id`), `POST /houses/<h>/rooms` (key `room_id`; house not found = 404; the room gets `default_thresholds`, see `store.new_room`), `POST /users` (keys `chat_id`, `name`, `houses`): `require(...)` the keys (400), `create(...)` (**409** if the id exists), then `save()` and answer **201** with the new object.
- `PUT /houses/<h>/<r>/thresholds`: room not found = 404; body must be a non-empty object with only `t_min`, `t_max`, `h_max` and finite numbers, else 400; **partial update** (keys not sent stay as they are); after the update `t_min` must be lower than `t_max`, else 400 and nothing changes.
- `POST /devices` (keys `house_id`, `room_id`, `type`, `sensors`, `actuators`; the last two must be lists, else 400): `find_device`: **409** if it exists; otherwise append the device, `ensure_room(...)` so the room exists, **201** and answer the *configuration of the device*: `{"device": <the object>, "broker": {host, port}, "base_topic": "smarthome/<house>/<room>", "interval": <seconds>}` (given as `self.device_config(device)`; `default_interval` is in the seed). `GET /devices/<h>/<r>/<type>` answers the same, for a device that restarts. The device needs nothing else to start.
- `PUT /users/<chat_id>` (keys `name`, `houses`): user not found = 404, else replace name and houses.
- `PUT /thingspeak`: keys `channel_id`, `fields`; replaces the section.
- Always `save()` after a change, inside the lock.

### Ex3 - Self-registering device connector (`device_connector.py`)
**Registering is the first thing a device does**: "I am here". In `main` the connector calls `dc.register(catalog)` before anything else: `POST {catalog}/devices` with
`{"house_id", "room_id", "type": "device_connector", "sensors": [names of the sensors], "actuators": [names of the actuators]}` (method `DeviceConnector.register`). If the answer is **409** the device already exists (a restart): `register` reads the same answer with `GET {catalog}/devices/<house>/<room>/device_connector`. Either way the catalog **answers with all the configuration the device needs** (broker, base topic, publish interval): `register` returns it, `main` prints it and uses `interval` (the `--interval` option overrides it). From L07 the broker of that answer is used to start MQTT: the only thing hard-coded in a device is the URL of the catalog. Show that **a brand new room appears in the catalog at runtime**: start `house1 garage` and read `GET /houses/house1`: the room `garage` is there, with the default thresholds, and no line of code was changed. Start it again: it gets 409 and still works.

### Ex4 - Catalog client (`catalog_client.py`)
With `requests`: list the houses and their rooms; read the thresholds of `house1/kitchen`; change `t_max` with a partial PUT; try an invalid PUT (`t_min` = 40) and print the 400; list the registered devices; POST the existing `house1` again and print the 409.

## How to run
All commands from inside `solution/` (or `starter/`), using the course virtual environment. Open one terminal per line, **in this order**:

```
1) python catalog.py                                   # port 8080, state in catalog_state.json
2) python device_connector.py house1 garage            # registers itself in the catalog
3) python catalog_client.py
```
Options: `python catalog.py 8120 my_state.json` (port, state file), `python device_connector.py house1 garage --catalog http://localhost:8120`, `python catalog_client.py http://localhost:8120`.

### curl examples
The header `Content-Type: application/json` is required on POST/PUT with a body in curl: without it curl sends the body as a web form and CherryPy answers 400 "Unexpected body parameters". (`requests` with `json=` sets it for you.)
```
curl localhost:8080/broker
curl localhost:8080/houses
curl localhost:8080/houses/house1/kitchen/thresholds
curl -X PUT -H "Content-Type: application/json" -d '{"t_max": 25}' localhost:8080/houses/house1/kitchen/thresholds
curl -X PUT -H "Content-Type: application/json" -d '{"t_min": 40}' localhost:8080/houses/house1/kitchen/thresholds     # 400
curl -X POST -H "Content-Type: application/json" -d '{"house_id":"house1","room_id":"attic","type":"device_connector","sensors":["temperature"],"actuators":[]}' localhost:8080/devices   # 201, again: 409
curl localhost:8080/devices/house1/attic/device_connector
curl -X POST -H "Content-Type: application/json" -d '{"house_id":"house1"}' localhost:8080/houses                          # 409
curl -X POST -H "Content-Type: application/json" -d '{"room_id":"pantry"}' localhost:8080/houses/house1/rooms
curl -X POST -H "Content-Type: application/json" -d '{"chat_id":1,"name":"Anna","houses":["house1"]}' localhost:8080/users
curl -X PUT -H "Content-Type: application/json" -d '{"name":"Anna","houses":["house1","house2"]}' localhost:8080/users/1
curl localhost:8080/houses/house9                                                                                      # 404
```
To start again from the seed: stop the catalog and delete `catalog_state.json`.
