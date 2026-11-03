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
        data = self.store.data
        with self.store.lock:
            if uri == ("broker",):
                return data["broker"]
            if uri == ("houses",):
                return data["houses"]
            if len(uri) == 2 and uri[0] == "houses":
                house = self.store.find_house(uri[1])
                if house is None:
                    raise cherrypy.HTTPError(404, f"House {uri[1]} not found")
                return house
            if len(uri) == 4 and uri[0] == "houses" and uri[3] == "thresholds":
                room = self.store.find_room(uri[1], uri[2])
                if room is None:
                    raise cherrypy.HTTPError(404, f"Room {uri[1]}/{uri[2]} not found")
                return room["thresholds"]
            if uri == ("devices",):
                return data["devices"]
            if len(uri) == 4 and uri[0] == "devices":
                device = self.store.find_device(*uri[1:])
                if device is None:
                    raise cherrypy.HTTPError(404, f"Device {'/'.join(uri[1:])} not found")
                return self.device_config(device)
            if uri == ("users",):
                return data["users"]
            if uri == ("thingspeak",):
                return data["thingspeak"]
        raise cherrypy.HTTPError(404, "Unknown endpoint")

    def device_config(self, device):
        """What a device needs to work, sent back when it registers: broker, its MQTT base topic, publish interval."""
        return {"device": device, "broker": self.store.data["broker"],
                "base_topic": f"smarthome/{device['house_id']}/{device['room_id']}",
                "interval": self.store.data.get("default_interval", 10)}

    @cherrypy.tools.json_out()
    def POST(self, *uri):
        obj = read_json_body()
        with self.store.lock:
            if uri == ("houses",):
                require(obj, "house_id")
                result = {"house_id": obj["house_id"], "rooms": []}  # rooms are added with POST .../rooms
                create(self.store.data["houses"], result, "house_id")
            elif len(uri) == 3 and uri[0] == "houses" and uri[2] == "rooms":
                require(obj, "room_id")
                house = self.store.find_house(uri[1])
                if house is None:
                    raise cherrypy.HTTPError(404, f"House {uri[1]} not found")
                result = self.store.new_room(obj["room_id"])
                create(house["rooms"], result, "room_id")
            elif uri == ("devices",):
                require(obj, "house_id", "room_id", "type", "sensors", "actuators")
                if not isinstance(obj["sensors"], list) or not isinstance(obj["actuators"], list):
                    raise cherrypy.HTTPError(400, "sensors and actuators must be lists")
                if self.store.find_device(obj["house_id"], obj["room_id"], obj["type"]) is not None:
                    raise cherrypy.HTTPError(409, "Device already registered")  # a restart: GET its answer
                device = {k: obj[k] for k in ("house_id", "room_id", "type", "sensors", "actuators")}
                self.store.data["devices"].append(device)
                self.store.ensure_room(device["house_id"], device["room_id"])
                result = self.device_config(device)
            elif uri == ("users",):
                require(obj, "chat_id", "name", "houses")
                result = obj
                create(self.store.data["users"], obj, "chat_id")
            else:
                raise cherrypy.HTTPError(404, "Unknown endpoint")
            self.store.save()
        cherrypy.response.status = 201
        return result

    @cherrypy.tools.json_out()
    def PUT(self, *uri):
        obj = read_json_body()
        with self.store.lock:
            if len(uri) == 4 and uri[0] == "houses" and uri[3] == "thresholds":
                room = self.store.find_room(uri[1], uri[2])
                if room is None:
                    raise cherrypy.HTTPError(404, f"Room {uri[1]}/{uri[2]} not found")
                # partial update: only known keys, only finite numbers
                if not isinstance(obj, dict) or not obj or any(
                    k not in THRESHOLD_KEYS or not isinstance(v, (int, float)) or not math.isfinite(v)
                    for k, v in obj.items()
                ):
                    raise cherrypy.HTTPError(400, f"Body: finite numbers for any of {THRESHOLD_KEYS}")
                new = {**room["thresholds"], **obj}
                if new["t_min"] >= new["t_max"]:
                    raise cherrypy.HTTPError(400, "t_min must be lower than t_max")
                room["thresholds"] = new
                result = room["thresholds"]
            elif len(uri) == 2 and uri[0] == "users":
                require(obj, "name", "houses")
                user = next((u for u in self.store.data["users"] if str(u["chat_id"]) == uri[1]), None)
                if user is None:
                    raise cherrypy.HTTPError(404, f"User {uri[1]} not found")
                user.update(name=obj["name"], houses=obj["houses"])
                result = user
            elif uri == ("thingspeak",):
                require(obj, "channel_id", "fields")
                self.store.data["thingspeak"] = obj
                result = obj
            else:
                raise cherrypy.HTTPError(404, "Unknown endpoint")
            self.store.save()
        return result


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
