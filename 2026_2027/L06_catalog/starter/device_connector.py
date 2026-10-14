"""Device connector of one room (v3-lite): REST only, no MQTT yet. Registers itself in the catalog at start-up.

Usage: python device_connector.py house1 garage 8085 [--catalog http://localhost:8080] [--interval 5]

REST   GET /        latest measurements + HVAC state
       PUT /hvac    body {"command": "ON"|"OFF"}
"""
import argparse
import json
import threading

import cherrypy
import requests

from devices import HVAC, HumiditySensor, TemperatureSensor


class DeviceConnector:
    exposed = True

    def __init__(self, house_id, room_id, sensors, hvac):
        self.house_id = house_id
        self.room_id = room_id
        self.sensors = sensors
        self.hvac = hvac
        self.latest = {}

    def read_sensors(self):
        self.latest = {s.name: s.sense() for s in self.sensors}
        return self.latest

    @cherrypy.tools.json_out()
    def GET(self, *uri):
        if uri:
            raise cherrypy.HTTPError(404, "Unknown endpoint")
        return {"house_id": self.house_id, "room_id": self.room_id,
                "measurements": self.latest, "hvac": self.hvac.state}

    @cherrypy.tools.json_out()
    def PUT(self, *uri):
        if uri != ("hvac",):
            raise cherrypy.HTTPError(404, "Unknown endpoint")
        try:
            self.hvac.actuate(json.loads(cherrypy.request.body.read())["command"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            raise cherrypy.HTTPError(400, f"Body must be {{\"command\": \"ON\"|\"OFF\"}} ({e})")
        return {"hvac": self.hvac.state}


def register(catalog, dc, port):
    """Tell the catalog who we are. The catalog creates the house/room if they do not exist."""
    raise NotImplementedError("TODO Ex3: build the registration dict and POST it to {catalog}/devices")


def main():
    parser = argparse.ArgumentParser(description="Device connector for one room")
    parser.add_argument("house_id")
    parser.add_argument("room_id")
    parser.add_argument("port", type=int)
    parser.add_argument("--catalog", default="http://localhost:8080")
    parser.add_argument("--interval", type=float, default=5, help="seconds between measurements")
    args = parser.parse_args()

    dc = DeviceConnector(args.house_id, args.room_id, [TemperatureSensor(), HumiditySensor()], HVAC())
    cherrypy.config.update({"server.socket_host": "0.0.0.0", "server.socket_port": args.port,
                            "log.screen": False})
    cherrypy.tree.mount(dc, "/", {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}})
    cherrypy.engine.start()
    register(args.catalog, dc, args.port)

    stop = threading.Event()
    try:
        while not stop.wait(args.interval):
            print(f"{args.house_id}/{args.room_id}: {dc.read_sensors()}")
    except KeyboardInterrupt:
        pass
    finally:
        cherrypy.engine.exit()


if __name__ == "__main__":
    main()
