"""Device connector of one room (v2): reads its sensors and registers itself in the catalog.
No REST server: measurements and commands will travel over MQTT in L07 (the catalog only tells who exists).
HEARTBEAT version: re-registers every 60 s with "last_seen".

Usage: python device_connector.py house1 garage [--catalog http://localhost:8080] [--interval 5]

The first thing a device does is to register: POST /devices "I am here". The catalog stores it and answers with
everything the device needs: {"device", "broker": {host, port}, "base_topic", "interval"}.
"""
import argparse
import threading
import time

import requests

from devices import HVAC, HumiditySensor, TemperatureSensor


class DeviceConnector:
    def __init__(self, house_id, room_id, sensors, hvac):
        self.house_id = house_id
        self.room_id = room_id
        self.sensors = sensors
        self.hvac = hvac

    def read_sensors(self):
        return {s.name: s.sense() for s in self.sensors}

    def register(self, catalog):
        """Tell the catalog who we are (it creates the house/room if new) and return its answer (the config)."""
        raise NotImplementedError("TODO Extra: like Ex3 registration, plus \"last_seen\": time.time()")


def heartbeat(catalog, dc, stop):
    """Register again every 60 s: the catalog updates last_seen (upsert)."""
    raise NotImplementedError("TODO Extra: every 60 s call dc.register() again (catch requests.RequestException)")


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
    threading.Thread(target=heartbeat, args=(args.catalog, dc, stop), daemon=True).start()
    try:
        while not stop.wait(interval):
            print(f"{args.house_id}/{args.room_id}: {dc.read_sensors()}")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
