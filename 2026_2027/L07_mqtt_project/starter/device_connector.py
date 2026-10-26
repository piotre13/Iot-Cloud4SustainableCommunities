"""Device Connector: one per room. Publishes T/H over MQTT and obeys HVAC commands. No REST server.

Run:
    python device_connector.py house1 kitchen [--source random|csv] [--interval 10]

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

from config import catalog_url
from mymqtt import MyMQTT
from senml import senml_record
from devices import HVAC, make_sensors


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
            # TODO Ex1: publish the record on f"{self.base_topic}/{sensor.name}" with self.mqtt
            raise NotImplementedError("TODO Ex1: publish the SenML record with self.mqtt.publish")
            print(f"{self.base_topic}/{sensor.name}: {record['e'][0]['v']} {sensor.unit}")

    # --- commands (MQTT) -> HVAC ---
    def publish_state(self):
        # TODO Ex1: publish {"state": self.hvac.state} on f"{self.base_topic}/hvac/state" with retain=True
        #           (retained: whoever subscribes later gets the current state at once)
        raise NotImplementedError("TODO Ex1: publish the HVAC state, retained")

    def actuate(self, command):
        self.hvac.actuate(command)
        self.publish_state()

    def notify(self, topic, payload):
        """Called by MyMQTT for every message on <base_topic>/hvac."""
        raise NotImplementedError("TODO Ex1: call self.actuate(payload['command']); ignore bad payloads")


def main():
    parser = argparse.ArgumentParser(description="Device connector for one room")
    parser.add_argument("house_id")
    parser.add_argument("room_id")
    parser.add_argument("--source", choices=["random", "csv"], default="random")
    parser.add_argument("--interval", type=float, default=None, help="seconds between measurements (default: from the catalog)")
    parser.add_argument("--catalog", default=None, help="catalog URL (default: settings.json)")
    args = parser.parse_args()
    catalog = args.catalog or catalog_url()

    dc = DeviceConnector(args.house_id, args.room_id, make_sensors(args.source), HVAC())

    config = dc.register(catalog)  # first thing: who we are -> broker, base topic, interval (as in L05)
    interval = args.interval or config["interval"]  # --interval overrides the catalog default
    # TODO Ex1: 1) create dc.mqtt = MyMQTT(client_id, host, port, notifier=dc) with the broker of `config`
    #           2) start it, subscribe to the hvac topic and call dc.publish_state()
    raise NotImplementedError("TODO Ex1: MQTT client built from the catalog answer")

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
