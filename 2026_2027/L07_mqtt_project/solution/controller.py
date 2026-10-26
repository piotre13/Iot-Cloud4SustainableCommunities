"""Controller: one instance for every house, thanks to MQTT wildcards.

Run:   python controller.py [--catalog URL]

Rules (thresholds read from the catalog at every message, so changes from the bot and new rooms
are seen without a restart):
    temperature < t_min -> HVAC ON      temperature > t_max -> HVAC OFF
    humidity    > h_max -> alert on smarthome/<house>/alerts
Commands and alerts are sent only when the situation changes, not at every measurement;
the HVAC state published by the connectors keeps the controller in sync.
"""
import argparse
import time

import requests

from config import catalog_url, get_broker
from mymqtt import MyMQTT


class Controller:
    def __init__(self, catalog):
        self.catalog = catalog
        self.mqtt = None
        self.last_command = {}  # (house, room) -> "ON" | "OFF"
        self.humid_rooms = set()  # rooms whose humidity is already above h_max

    def get_thresholds(self, house, room):
        r = requests.get(f"{self.catalog}/houses/{house}/{room}/thresholds", timeout=5)
        r.raise_for_status()
        return r.json()

    def notify(self, topic, payload):
        if topic.endswith("/hvac/state"):
            # The HVAC changed state outside our control (REST command, restart), or this is a late
            # message about an older command: forget our last command, the next reading decides again.
            _, house, room, _, _ = topic.split("/")
            if payload.get("state") != self.last_command.get((house, room)):
                self.last_command.pop((house, room), None)
            return
        try:
            _, house, room, kind = topic.split("/")
            value = float(payload["e"][0]["v"])  # SenML: first (only) entry
            thresholds = self.get_thresholds(house, room)
        except (ValueError, KeyError, TypeError, requests.RequestException) as e:
            print(f"Skipped {topic}: {e}")
            return
        if kind == "temperature":
            self.check_temperature(house, room, value, thresholds)
        elif kind == "humidity":
            self.check_humidity(house, room, value, thresholds)

    def check_temperature(self, house, room, value, thresholds):
        if value < thresholds["t_min"]:
            command = "ON"
        elif value > thresholds["t_max"]:
            command = "OFF"
        else:
            return  # inside the band: leave the HVAC as it is
        if self.last_command.get((house, room)) != command:
            self.last_command[(house, room)] = command
            self.mqtt.publish(f"smarthome/{house}/{room}/hvac", {"command": command})
            print(f"{house}/{room}: {value} Cel -> HVAC {command}")

    def check_humidity(self, house, room, value, thresholds):
        if value > thresholds["h_max"]:
            if (house, room) not in self.humid_rooms:
                self.humid_rooms.add((house, room))
                msg = f"humidity {value:g}% > {thresholds['h_max']}%"
                self.mqtt.publish(f"smarthome/{house}/alerts", {"room": room, "msg": msg})
                print(f"{house}/{room}: ALERT {msg}")
        else:
            self.humid_rooms.discard((house, room))


def main():
    parser = argparse.ArgumentParser(description="Threshold controller for all houses")
    parser.add_argument("--catalog", default=None, help="catalog URL (default: settings.json)")
    args = parser.parse_args()
    catalog = args.catalog or catalog_url()

    controller = Controller(catalog)
    broker = get_broker(catalog)
    controller.mqtt = MyMQTT("controller", broker["host"], broker["port"], notifier=controller)
    controller.mqtt.start()
    controller.mqtt.subscribe("smarthome/+/+/temperature")
    controller.mqtt.subscribe("smarthome/+/+/humidity")
    controller.mqtt.subscribe("smarthome/+/+/hvac/state")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.mqtt.stop()


if __name__ == "__main__":
    main()
