"""Build one DeviceConnector + one Controller for every room in config.json, then loop.

Usage: python main.py [cycles]
"""
import json
import sys
import time

from controller import Controller
from device_connector import DeviceConnector
from devices import HVAC, HumiditySensor, TemperatureSensor


def build_rooms(path="config.json"):
    raise NotImplementedError("TODO Ex7: read config.json; for every room build a DeviceConnector (random sensors + HVAC) and a Controller; return a list of (connector, controller)")


def main():
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    rooms = build_rooms()
    for cycle in range(1, cycles + 1):
        print(f"--- cycle {cycle} ---")
        for connector, controller in rooms:
            measurements = connector.read_sensors()
            command, alert = controller.decide(measurements)
            print(f"{connector.house_id}/{connector.room_id}: {measurements}")
            if command is not None and command != connector.hvac.state:
                connector.actuate(command)
            if alert:
                print(f"ALERT {connector.house_id}/{connector.room_id}: {alert}")
        time.sleep(1)


if __name__ == "__main__":
    main()
