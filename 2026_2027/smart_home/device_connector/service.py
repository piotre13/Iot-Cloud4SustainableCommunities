"""Device Connector: one per room. Publishes T/H over MQTT and obeys HVAC commands. No REST server.

Run from smart_home/:
    python -m device_connector.service house1 kitchen [--source random|csv] [--interval 10]

The first thing it does is to register itself in the catalog (POST /devices): a new room is created there
automatically, so adding a room at runtime = launching one more connector. The answer of the catalog is all the
configuration the device needs: broker, MQTT base topic, publish interval. Nothing else is hard-coded.

MQTT   pub smarthome/<house>/<room>/temperature, /humidity (SenML)
       sub smarthome/<house>/<room>/hvac          {"command": "ON"}
       pub smarthome/<house>/<room>/hvac/state    {"state": "ON"}  retained: at start-up and after every actuation
"""
import argparse
import time

import requests

from common.config import catalog_url
from common.mymqtt import MyMQTT
from common.senml import senml_record
from device_connector.devices import HVAC, make_sensors


class DeviceConnector:
    def __init__(self, house_id, room_id, sensors, hvac):
        self.house_id = house_id
        self.room_id = room_id
        self.sensors = sensors
        self.hvac = hvac
        self.base_topic = None  # given by the catalog when we register
        self.mqtt = None

    # --- registration: the first thing a device does ---
    def register(self, catalog):
        """POST /devices: "I am here". The catalog stores us (and creates the house/room if new) and answers
        with everything we need: {"device", "broker": {host, port}, "base_topic", "interval"}."""
        registration = {"device_id": f"dc_{self.house_id}_{self.room_id}", "house_id": self.house_id,
                        "room_id": self.room_id, "sensors": [s.name for s in self.sensors]}
        r = requests.post(f"{catalog}/devices", json=registration, timeout=5)
        r.raise_for_status()
        config = r.json()
        self.base_topic = config["base_topic"]
        print(f"Registered {registration['device_id']} in the catalog: {config}")
        return config

    # --- sensors -> MQTT ---
    def publish_measurements(self):
        for sensor in self.sensors:
            record = senml_record(f"{self.house_id}/{self.room_id}", sensor.name, sensor.unit, sensor.sense())
            self.mqtt.publish(f"{self.base_topic}/{sensor.name}", record)
            print(f"{self.base_topic}/{sensor.name}: {record['e'][0]['v']} {sensor.unit}")

    # --- commands (MQTT) -> HVAC ---
    def publish_state(self):
        # retained: whoever subscribes later (e.g. the bot) gets the current state at once
        self.mqtt.publish(f"{self.base_topic}/hvac/state", {"state": self.hvac.state}, retain=True)

    def actuate(self, command):
        self.hvac.actuate(command)
        self.publish_state()

    def notify(self, topic, payload):
        """Called by MyMQTT for every message on <base_topic>/hvac."""
        try:
            self.actuate(payload["command"])
        except (KeyError, TypeError, ValueError) as e:
            print(f"Ignored bad command {payload}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Device connector for one room")
    parser.add_argument("house_id")
    parser.add_argument("room_id")
    parser.add_argument("--source", choices=["random", "csv"], default="random")
    parser.add_argument("--interval", type=float, default=None, help="seconds between measurements (default: from the catalog)")
    parser.add_argument("--catalog", default=None, help="catalog URL (default: config/settings.json)")
    args = parser.parse_args()
    catalog = args.catalog or catalog_url()

    dc = DeviceConnector(args.house_id, args.room_id, make_sensors(args.source), HVAC())

    config = dc.register(catalog)  # first thing: who we are -> broker, base topic, interval
    interval = args.interval or config["interval"]  # --interval overrides the catalog default
    broker = config["broker"]
    dc.mqtt = MyMQTT(f"dc_{args.house_id}_{args.room_id}", broker["host"], broker["port"], notifier=dc)
    dc.mqtt.start()
    dc.mqtt.subscribe(f"{dc.base_topic}/hvac")
    dc.publish_state()

    try:
        while True:
            dc.publish_measurements()
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        dc.mqtt.stop()


if __name__ == "__main__":
    main()
