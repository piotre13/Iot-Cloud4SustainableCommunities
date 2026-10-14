"""Device Connector: one per room. Publishes T/H over MQTT, obeys HVAC commands, exposes REST.

Run from smart_home/:
    python -m device_connector.service house1 kitchen 8081 [--source random|csv] [--interval 10]

At start-up it asks the catalog for the broker and registers itself (POST /devices): a new room is created
in the catalog automatically, so adding a room at runtime = launching one more connector.

REST   GET /        latest measurements + HVAC state
       PUT /hvac    body {"command": "ON"|"OFF"}
MQTT   pub smarthome/<house>/<room>/temperature, /humidity (SenML)
       sub smarthome/<house>/<room>/hvac          {"command": "ON"}
       pub smarthome/<house>/<room>/hvac/state    {"state": "ON"}  after every actuation
"""
import argparse
import json
import time

import cherrypy
import requests

from common.config import catalog_url, get_broker
from common.mymqtt import MyMQTT
from common.senml import senml_record
from device_connector.devices import HVAC, make_sensors


class DeviceConnector:
    exposed = True

    def __init__(self, house_id, room_id, sensors, hvac):
        self.house_id = house_id
        self.room_id = room_id
        self.sensors = sensors
        self.hvac = hvac
        self.base_topic = f"smarthome/{house_id}/{room_id}"
        self.latest = {}  # sensor name -> last SenML record
        self.mqtt = None

    # --- sensors -> MQTT ---
    def publish_measurements(self):
        for sensor in self.sensors:
            record = senml_record(f"{self.house_id}/{self.room_id}", sensor.name, sensor.unit, sensor.sense())
            self.latest[sensor.name] = record
            self.mqtt.publish(f"{self.base_topic}/{sensor.name}", record)
            print(f"{self.base_topic}/{sensor.name}: {record['e'][0]['v']} {sensor.unit}")

    # --- commands (MQTT or REST) -> HVAC ---
    def actuate(self, command):
        self.hvac.actuate(command)
        self.mqtt.publish(f"{self.base_topic}/hvac/state", {"state": self.hvac.state})

    def notify(self, topic, payload):
        """Called by MyMQTT for every message on <base_topic>/hvac."""
        try:
            self.actuate(payload["command"])
        except (KeyError, TypeError, ValueError) as e:
            print(f"Ignored bad command {payload}: {e}")

    # --- REST ---
    @cherrypy.tools.json_out()
    def GET(self, *uri):
        if uri:
            raise cherrypy.HTTPError(404, "Unknown endpoint")
        return {"house_id": self.house_id, "room_id": self.room_id,
                "measurements": list(self.latest.values()), "hvac": self.hvac.state}

    @cherrypy.tools.json_out()
    def PUT(self, *uri):
        if uri != ("hvac",):
            raise cherrypy.HTTPError(404, "Unknown endpoint")
        try:
            self.actuate(json.loads(cherrypy.request.body.read())["command"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            raise cherrypy.HTTPError(400, f"Body must be {{\"command\": \"ON\"|\"OFF\"}} ({e})")
        return {"hvac": self.hvac.state}


def main():
    parser = argparse.ArgumentParser(description="Device connector for one room")
    parser.add_argument("house_id")
    parser.add_argument("room_id")
    parser.add_argument("port", type=int)
    parser.add_argument("--source", choices=["random", "csv"], default="random")
    parser.add_argument("--interval", type=float, default=10, help="seconds between measurements")
    parser.add_argument("--catalog", default=None, help="catalog URL (default: config/settings.json)")
    args = parser.parse_args()
    catalog = args.catalog or catalog_url()

    dc = DeviceConnector(args.house_id, args.room_id, make_sensors(args.source), HVAC())

    cherrypy.config.update({"server.socket_host": "0.0.0.0", "server.socket_port": args.port,
                            "log.screen": False})
    cherrypy.tree.mount(dc, "/", {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}})
    cherrypy.engine.start()

    broker = get_broker(catalog)
    dc.mqtt = MyMQTT(f"dc_{args.house_id}_{args.room_id}", broker["host"], broker["port"], notifier=dc)
    dc.mqtt.start()
    dc.mqtt.subscribe(f"{dc.base_topic}/hvac")

    registration = {"device_id": f"dc_{args.house_id}_{args.room_id}", "house_id": args.house_id,
                    "room_id": args.room_id, "rest_url": f"http://localhost:{args.port}",
                    "sensors": [s.name for s in dc.sensors]}
    requests.post(f"{catalog}/devices", json=registration, timeout=5).raise_for_status()
    print(f"Registered {registration['device_id']} in the catalog")

    try:
        while True:
            dc.publish_measurements()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        dc.mqtt.stop()
        cherrypy.engine.exit()


if __name__ == "__main__":
    main()
