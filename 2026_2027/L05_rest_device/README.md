# L05 - REST server for the device

## Goals
- Give the device connector of L03 a REST interface with CherryPy.
- Write a client with `requests` that reads a room and switches its HVAC.

## Theory in 5 minutes
**What is a resource here?** A room is a thing you can look at, so `/` is the room (its measurements and the HVAC state).
The HVAC of that room is a thing with a state, so `/hvac` is a resource too.

**Why PUT for the HVAC?** We do not say "toggle", we say "the state of the HVAC must be ON". Repeating the same
request gives the same result (PUT is idempotent). A toggle would give a different result every time: a lost
answer plus a retry would flip the HVAC back.

**Status codes**
| Code | When |
|---|---|
| 200 | all fine |
| 400 | the request is wrong: body is not JSON, no `command`, command not ON/OFF |
| 404 | the path does not exist (e.g. `/foo`) |

**Fresh values.** `GET /` calls `read_sensors()` at every request: values are always fresh and we need no background
loop. In L06 the connector will publish by itself with MQTT, and GET will return the latest published values.

**Note.** In the final project `measurements` is a list of SenML records. Here it is a simple dict
`{"temperature": 21.3, "humidity": 55.0}`: SenML arrives in L07. The REST semantics (GET /, PUT /hvac, codes) are the same.

## Files
- `devices.py` - same as L03, unchanged.
- `device_connector.py` - Ex1.
- `client.py` - Ex2.

## Exercises
**Ex1 - REST device connector** (`device_connector.py`)
The `DeviceConnector` class is the one of L03. Add the REST interface (`exposed = True`, `GET`, `PUT`):
- `GET /` returns `{"house_id", "room_id", "measurements": {...}, "hvac": "ON"|"OFF"}`.
- `PUT /hvac` with body `{"command": "ON"|"OFF"}` switches the HVAC and returns `{"hvac": state}`.
- invalid JSON or invalid command -> 400; any other path -> 404.

**Ex2 - client** (`client.py`)
Given the base URL(s) as argument: `GET` the room and print it, then `PUT /hvac` with `ON` if the temperature is
below 19 Cel (too cold: heating on), `OFF` otherwise. Print the status code of the PUT.

**Extra (optional)** - two rooms
Start two connectors (two ports) and run the client with both URLs; it already loops over the list.

## How to run
Always from inside `solution/` (or `starter/`).

Terminal 1 (connector):
```
python device_connector.py house1 kitchen 8081
```
Terminal 2 (client):
```
python client.py http://localhost:8081
```
Extra, three terminals:
```
python device_connector.py house1 kitchen 8081
python device_connector.py house1 bedroom 8082
python client.py http://localhost:8081 http://localhost:8082
```

curl:
```
curl http://localhost:8081/
curl -X PUT -H "Content-Type: application/json" -d '{"command": "ON"}' http://localhost:8081/hvac
curl -i -X PUT -H "Content-Type: application/json" -d '{"command": "HEATING"}' http://localhost:8081/hvac    # 400
curl -i http://localhost:8081/foo                                         # 404
```

Without the `Content-Type: application/json` header curl sends the body as a web form and CherryPy answers 400
before our code runs. `requests.put(url, json=...)` sets the header for you.
