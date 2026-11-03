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
import time

import requests
from devices import HVAC, HumiditySensor, TemperatureSensor

DEVICE_TYPE = "device_connector"


class DeviceConnector:
    def __init__(self, house_id, room_id, sensors, hvac):
        self.house_id = house_id
        self.room_id = room_id
        self.sensors = sensors
        self.hvac = hvac
        self.config = None  # will be filled by register()

    def read_sensors(self):
        return {s.name: s.sense() for s in self.sensors}

    def register(self, catalog):
        """Tell the catalog who we are (it creates the house/room if new) and return its answer (the config).
        409 = already registered (a restart): the same answer is read with a GET."""
        raise NotImplementedError(
            "TODO Ex3: POST {catalog}/devices with {house_id, room_id, type, sensors: names of self.sensors, actuators: [self.hvac.name]}; on 409 GET {catalog}/devices/<house>/<room>/<DEVICE_TYPE>; return the JSON answer"
        )


# def main():
#     parser = argparse.ArgumentParser(description="Device connector for one room")
#     parser.add_argument("house_id")
#     parser.add_argument("room_id")
#     parser.add_argument("--catalog", default="http://localhost:8080")
#     parser.add_argument("--interval", type=float, default=None, help="seconds between measurements (default: from the catalog)")
#     args = parser.parse_args()

#     dc = DeviceConnector(args.house_id, args.room_id, [TemperatureSensor(), HumiditySensor()], HVAC())
#     config = dc.register(args.catalog)  # the first thing a device does
#     print(f"Configuration received from the catalog: {config}")
#     interval = args.interval or config["interval"]

#     stop = threading.Event()
#     try:
#         while not stop.wait(interval):
#             print(f"{args.house_id}/{args.room_id}: {dc.read_sensors()}")
#     except KeyboardInterrupt:
#         pass


def main():
    catalog = (
        input("Enter catalog URL (default: http://localhost:8080): ")
        or "http://localhost:8080"
    )

    while True:
        try:
            print(f"Registering device in catalog {catalog}...")
            house_id = input("Enter house ID: ")
            room_id = input("Enter room ID: ")
            interval = input(
                "Enter measurement interval (seconds, default: from catalog): "
            )

            dc = DeviceConnector(
                house_id, room_id, [TemperatureSensor(), HumiditySensor()], HVAC()
            )

            config = dc.register(catalog)  # the first thing a device does
            print(f"Configuration received from the catalog: {config}")
            interval = float(interval) if interval else config["interval"]

            while True:
                print(f"{house_id}/{room_id}: {dc.read_sensors()}")
                time.sleep(interval)

        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
