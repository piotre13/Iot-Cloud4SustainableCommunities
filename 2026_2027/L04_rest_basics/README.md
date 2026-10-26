# L04 - REST basics: `requests` client and CherryPy server (3 h)

Module produced: **CherryPy base**. The same patterns are reused in L05 (device connector REST) and L06 (catalog).

## Goals
- Understand HTTP and REST (resources, URIs, methods, status codes).
- Call a public REST API from Python with `requests`.
- Write a small REST service with CherryPy and test it with a client.

## Short theory

**HTTP** is request/response: the client sends *method + URI + headers + (optional) body*, the server answers *status code + headers + body*.

**Resource and URI**: everything is a "thing" with an address, e.g. `http://localhost:8080/add?a=1&b=2`
(`/add` = path, `?a=1&b=2` = query parameters).

| Method | Meaning | Typical use |
|--------|---------|-------------|
| GET | read | get a resource, no body |
| POST | create / send data | JSON body |
| PUT | update (replace) | JSON body |
| DELETE | remove | no body |

**Status codes**: `200` OK, `201` created, `400` bad request (client error: missing/invalid data), `404` not found, `500` server error (our bug).

**Query params vs JSON body**: small, optional, "what to look for" values go in the query string (`?name=Anna`). Structured data to create/change goes in a JSON body, with header `Content-Type: application/json`.

**JSON**: text format for dicts/lists/numbers/strings. In Python `response.json()` and `json=` do the conversion for you.

### `requests` (client)
```python
r = requests.get(url, params={"a": 1}, timeout=10)   # ?a=1 added automatically
r.raise_for_status()      # raises HTTPError for 4xx/5xx
data = r.json()
r = requests.post(url, json={"x": 1}, timeout=10)    # sets the JSON body and header
```
Always set `timeout`: without it a dead server blocks your program forever.

### CherryPy (server)
- A class with `exposed = True` is a resource; with `cherrypy.dispatch.MethodDispatcher()` the HTTP method selects the Python method: `GET`, `POST`, `PUT`, `DELETE`.
- `def GET(self, *uri, **params)`: `uri` = tuple of path segments after the mount point (`/add/x` -> `("add", "x")`), `params` = query parameters (always **strings**).
- `@cherrypy.tools.json_out()` turns the returned dict into JSON; `@cherrypy.tools.json_in()` parses the body into `cherrypy.request.json`.
- Errors: `raise cherrypy.HTTPError(400, "clear message")`.
- Same style as the course project: see `smart_home/catalog/service.py`.

## How to run
Use the course virtual environment (`cherrypy`, `requests` installed). Run every script from inside the folder:
```
cd solution            # or starter
python ex1_citybikes_client.py Milano
python hello_world.py 8080          # port is optional, default 8080
python ex2_calculator.py 8080
python ex2_client.py http://localhost:8080     # in a second terminal, with the server running
```
Browser/curl test: `curl "http://localhost:8080/add?a=1&b=2"`.

**Starters**: every `TODO` is a `raise NotImplementedError("TODO ...")`. For the CherryPy classes the raise is inside `GET`/`POST`, so the server starts normally and the request answers `500` with the TODO text in the page: read it in the browser or the server log. Replace the raise with your code.

## Exercises

### Ex1 - CityBikes client (`ex1_citybikes_client.py`)
Public API: `https://api.citybik.es/v2/networks`. Given a city on the command line (default `Milano`):
1. Get the list of networks and keep those whose `location.city` matches the city (ignore upper/lower case).
2. For each network get its stations (`href` field) and print name, free bikes, empty slots.
3. Handle timeouts and HTTP errors (`timeout=10`, `raise_for_status`) without crashing; print a message when no network is found.

Note: at the time of writing CityBikes has **no network for Torino** (the script says so); try `Milano`, `Barcelona`, `Paris`.

### HelloWorld (`hello_world.py`)
CherryPy server: `GET /` returns `Hello World`; `GET /?name=Anna` returns `Hello Anna`. Test with browser and curl.

### Ex2 - Calculator service (`ex2_calculator.py`, `ex2_client.py`)
- `GET /add?a=1&b=2` (also `sub`, `mul`, `div`) -> `{"operation": "add", "a": 1.0, "b": 2.0, "result": 3.0}`
- `POST /` with body `{"operation": "add", "operands": [1, 2, 3]}` -> `{"operation": "add", "operands": [1.0, 2.0, 3.0], "result": 6.0}` (operations applied left to right).
- Errors must be explicit: missing/non-numeric parameter, unknown operation in POST, division by zero -> `400` with a clear message; unknown path -> `404`.
- `ex2_client.py [base_url]` calls the service with `requests` (GET, POST, and some error cases) and prints the results.

Typical mistakes of the 2025 version, fixed here: missing parameters silently replaced by default values (4) or giving `None`/an empty answer; no error for an unknown operation; division by zero checked on a string (`b != 0` with `b` = `"0"`) and answered with a text; mixed text and JSON responses; one class per operation instead of one resource.

