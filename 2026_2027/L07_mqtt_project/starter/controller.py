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
        # TODO Ex2: three kinds of topic arrive here
        #   .../hvac/state -> remember payload["state"] in self.last_command[(house, room)]
        #   .../temperature -> get_thresholds + check_temperature
        #   .../humidity    -> get_thresholds + check_humidity
        raise NotImplementedError("TODO Ex2: dispatch the message by topic")

    def check_temperature(self, house, room, value, thresholds):
        # TODO Ex2: below t_min -> "ON", above t_max -> "OFF", otherwise nothing.
        # Publish {"command": ...} on smarthome/<house>/<room>/hvac only if it differs from self.last_command
        raise NotImplementedError("TODO Ex2: temperature rule")

    def check_humidity(self, house, room, value, thresholds):
        # TODO Ex2: above h_max -> ONE alert on smarthome/<house>/alerts {"room", "msg"} (use self.humid_rooms)
        raise NotImplementedError("TODO Ex2: humidity rule")


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
