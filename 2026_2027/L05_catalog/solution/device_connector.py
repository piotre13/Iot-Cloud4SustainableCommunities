"""Device connector of one room (v2): reads its sensors and registers itself in the catalog.
No REST server: measurements and commands will travel over MQTT in L07 (the catalog only tells who exists).

Usage: python device_connector.py house1 garage [--catalog http://localhost:8080] [--interval 5]

The first thing a device does is to register: POST /devices "I am here": house, room and type are the only
things hard-coded in the device, which then tells the catalog what it handles ({"sensors": [...],
"actuators": [...]}). The catalog stores it and answers with everything the device needs:
{"device", "broker": {host, port}, "base_topic", "interval"}.
"""
import argparse
import threading

import requests

from devices import HVAC, HumiditySensor, TemperatureSensor

DEVICE_TYPE = "device_connector"


class DeviceConnector:
    def __init__(self, house_id, room_id, sensors, hvac):
        self.house_id = house_id
        self.room_id = room_id
        self.sensors = sensors
        self.hvac = hvac

    def read_sensors(self):
        return {s.name: s.sense() for s in self.sensors}

    def register(self, catalog):
        """Tell the catalog who we are (it creates the house/room if new) and return its answer (the config).
        409 = already registered (a restart): the same answer is read with a GET."""
        device = {"house_id": self.house_id, "room_id": self.room_id, "type": DEVICE_TYPE,
                  "sensors": [s.name for s in self.sensors], "actuators": [self.hvac.name]}
        r = requests.post(f"{catalog}/devices", json=device, timeout=5)
        if r.status_code == 409:  # already registered (a restart): the same answer is there to read
            r = requests.get(f"{catalog}/devices/{self.house_id}/{self.room_id}/{DEVICE_TYPE}", timeout=5)
        r.raise_for_status()
        print(f"Registered {self.house_id}/{self.room_id} in the catalog")
        return r.json()


def main():
    parser = argparse.ArgumentParser(description="Device connector for one room")
    parser.add_argument("house_id")
    parser.add_argument("room_id")
    parser.add_argument("--catalog", default="http://localhost:8080")
    parser.add_argument("--interval", type=float, default=None, help="seconds between measurements (default: from the catalog)")
    args = parser.parse_args()

    dc = DeviceConnector(args.house_id, args.room_id, [TemperatureSensor(), HumiditySensor()], HVAC())
    config = dc.register(args.catalog)  # the first thing a device does
    print(f"Configuration received from the catalog: {config}")
    interval = args.interval or config["interval"]

    stop = threading.Event()
    try:
        while not stop.wait(interval):
            print(f"{args.house_id}/{args.room_id}: {dc.read_sensors()}")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
