"""Home Catalog: a REST service (CherryPy) that stores the description of the whole system in a JSON file.

Run:   python catalog.py [port] [state_file]
Default: port 8080, state file catalog_state.json (copied from the seed catalog.json at first start).

  GET  /broker
  GET  /houses                              POST /houses            (body: {house_id}; 409 if it exists)
  GET  /houses/<house_id>                   POST /houses/<house_id>/rooms   (body: {room_id}; default thresholds; 409 if it exists)
  GET  /houses/<house_id>/<room_id>/thresholds
  PUT  /houses/<house_id>/<room_id>/thresholds   (body: any of t_min, t_max, h_max)
  GET  /devices                             POST /devices           (body: {house_id, room_id, type, sensors, actuators}:
                                            "I am here". Creates house/room if new; 409 if the device exists)
                                            answer: {"device", "broker", "base_topic", "interval"}, all that the
                                            device needs to start (the device registers first)
  GET  /devices/<house_id>/<room_id>/<type>   the same answer, for a device that restarts (its POST got 409)
  GET  /users                               POST /users           (body: {chat_id, name, houses}; 409 if it exists)
                                            PUT  /users/<chat_id> (body: {name, houses}; 404 if unknown)
  GET  /thingspeak                          PUT  /thingspeak      (body: {channel_id, fields})
"""
import json
import math
import os
import shutil
import sys
import threading
from pathlib import Path

import cherrypy

HERE = Path(__file__).parent
SEED_PATH = HERE / "catalog.json"
THRESHOLD_KEYS = ("t_min", "t_max", "h_max")


class CatalogStore:
    """The catalog content in memory + atomic save to disk. One lock: CherryPy serves requests in threads."""

    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            shutil.copy(SEED_PATH, self.path)  # first run: start from the clean seed
        with open(self.path, encoding="utf-8") as f:
            self.data = json.load(f)
        self.lock = threading.RLock()

    def save(self):
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        os.replace(tmp, self.path)  # atomic: a crash never leaves half a file

    def find_house(self, house_id):
        return next((h for h in self.data["houses"] if h["house_id"] == house_id), None)

    def find_room(self, house_id, room_id):
        house = self.find_house(house_id)
        if house is None:
            return None
        return next((r for r in house["rooms"] if r["room_id"] == room_id), None)

    def find_device(self, house_id, room_id, device_type):
        return next((d for d in self.data["devices"]
                     if (d["house_id"], d["room_id"], d["type"]) == (house_id, room_id, device_type)), None)

    def new_room(self, room_id):
        return {"room_id": room_id, "thresholds": dict(self.data["default_thresholds"])}

    def ensure_room(self, house_id, room_id):
        """Create house and room with the default thresholds if they are missing."""
        house = self.find_house(house_id)
        if house is None:
            house = {"house_id": house_id, "rooms": []}
            self.data["houses"].append(house)
        room = self.find_room(house_id, room_id)
        if room is None:
            room = self.new_room(room_id)
            house["rooms"].append(room)
        return room


def read_json_body():
    try:
        return json.loads(cherrypy.request.body.read() or b"{}")
    except json.JSONDecodeError:
        raise cherrypy.HTTPError(400, "Invalid JSON")


def require(obj, *keys):
    if not isinstance(obj, dict):
        raise cherrypy.HTTPError(400, "Body must be a JSON object")
    missing = [k for k in keys if k not in obj]
    if missing:
        raise cherrypy.HTTPError(400, f"Missing keys: {missing}")


def create(items, obj, key):
    """Append the new item: 409 if one with the same key already exists (nothing is replaced)."""
    if any(item[key] == obj[key] for item in items):
        raise cherrypy.HTTPError(409, f"{key} {obj[key]} already exists")
    items.append(obj)


class CatalogAPI:
    exposed = True

    def __init__(self, store):
        self.store = store

    @cherrypy.tools.json_out()
    def GET(self, *uri):
        raise NotImplementedError("TODO Ex1: answer every GET endpoint listed in the module docstring (data, 404 if not found; a device: the answer self.device_config(device)), inside the lock")

    def device_config(self, device):
        """What a device needs to work, sent back when it registers: broker, its MQTT base topic, publish interval."""
        return {"device": device, "broker": self.store.data["broker"],
                "base_topic": f"smarthome/{device['house_id']}/{device['room_id']}",
                "interval": self.store.data.get("default_interval", 10)}

    @cherrypy.tools.json_out()
    def POST(self, *uri):
        raise NotImplementedError("TODO Ex2: POST houses, houses/<h>/rooms, users, devices: require() the keys, create() or 409 if it exists, save(), status 201, answer with the new object (a device: ensure_room, answer self.device_config(device))")

    @cherrypy.tools.json_out()
    def PUT(self, *uri):
        raise NotImplementedError("TODO Ex2: PUT thresholds (404 room, 400 bad body, partial update, t_min < t_max), users/<chat_id> (404), thingspeak, then save()")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    state_path = sys.argv[2] if len(sys.argv) > 2 else HERE / "catalog_state.json"
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}}
    cherrypy.config.update({"server.socket_host": "0.0.0.0", "server.socket_port": port})
    cherrypy.tree.mount(CatalogAPI(CatalogStore(state_path)), "/", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == "__main__":
    main()
