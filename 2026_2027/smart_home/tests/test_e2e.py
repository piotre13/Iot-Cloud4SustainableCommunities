"""End-to-end test: mosquitto + catalog + controller + device connectors, all as real processes.

Run from smart_home/:  python -m tests.test_e2e

The connectors publish random values only once (--interval 3600); the test then injects chosen
measurements with its own MQTT client, so every threshold crossing is deterministic.
"""
import json
import queue
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

from common.mymqtt import MyMQTT
from common.senml import senml_record
from tests.test_catalog import PORT as CATALOG_PORT, URL as CATALOG
from tests.test_common import MQTT_PORT, Collector, start_broker

SEED = Path(__file__).parent.parent / "catalog" / "catalog.json"


def spawn(*args):
    return subprocess.Popen([sys.executable, "-m", *args], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_until(check, timeout=5, what="condition"):
    end = time.time() + timeout
    while time.time() < end:
        try:
            if check():
                return
        except requests.RequestException:
            pass
        time.sleep(0.1)
    raise AssertionError(f"timed out waiting for {what}")


class Watcher(Collector):
    """MQTT probe: alerts go to the queue, the retained/published HVAC states are remembered."""

    def __init__(self):
        super().__init__()
        self.hvac = {}  # (house, room) -> "ON" | "OFF"

    def notify(self, topic, payload):
        if topic.endswith("/hvac/state"):
            self.hvac[tuple(topic.split("/")[1:3])] = payload["state"]
        else:
            super().notify(topic, payload)


def start_connector(house, room):
    proc = spawn("device_connector.service", house, room, "--interval", "3600", "--catalog", CATALOG)
    wait_until(lambda: requests.get(f"{CATALOG}/devices/dc_{house}_{room}", timeout=1).ok, what=f"{house}/{room} registration")
    return proc


def main():
    procs = []
    with tempfile.TemporaryDirectory() as tmp:
        state = json.loads(SEED.read_text())
        state["broker"]["port"] = MQTT_PORT
        (Path(tmp) / "state.json").write_text(json.dumps(state))
        probe = None
        try:
            procs.append(start_broker())
            procs.append(spawn("catalog.service", str(CATALOG_PORT), str(Path(tmp) / "state.json")))
            wait_until(lambda: requests.get(f"{CATALOG}/broker", timeout=1).ok, what="catalog")
            procs.append(spawn("controller.service", "--catalog", CATALOG))
            time.sleep(1)
            procs.append(start_connector("house1", "kitchen"))
            procs.append(start_connector("house2", "bedroom"))
            time.sleep(1)  # let the start-up random readings settle

            collector = Watcher()
            probe = MyMQTT("probe", "localhost", MQTT_PORT, notifier=collector)
            probe.start()
            probe.subscribe("smarthome/+/alerts")
            probe.subscribe("smarthome/+/+/hvac/state")  # retained: the current state arrives at once
            time.sleep(0.5)

            def hvac_state(house, room):
                return collector.hvac.get((house, room))

            def send(house, room, kind, value):
                probe.publish(f"smarthome/{house}/{room}/{kind}", senml_record(f"{house}/{room}", kind, "", value))

            # 1. thresholds of house1/kitchen are 19..23
            send("house1", "kitchen", "temperature", 10)
            wait_until(lambda: hvac_state("house1", "kitchen") == "ON", what="kitchen ON")
            send("house1", "kitchen", "temperature", 30)
            wait_until(lambda: hvac_state("house1", "kitchen") == "OFF", what="kitchen OFF")
            # the other house is untouched by kitchen messages, and reacts to its own
            send("house2", "bedroom", "temperature", 10)
            wait_until(lambda: hvac_state("house2", "bedroom") == "ON", what="house2 bedroom ON")

            # 2. humidity alert, sent once while it stays high (50 first: the random start-up value may be high)
            send("house1", "kitchen", "humidity", 50)
            send("house1", "kitchen", "humidity", 90)
            topic, alert = collector.messages.get(timeout=3)
            assert topic == "smarthome/house1/alerts" and alert["room"] == "kitchen", alert
            send("house1", "kitchen", "humidity", 91)
            time.sleep(1)
            assert collector.messages.empty(), "second alert while still humid"

            # 3. a threshold changed in the catalog (what the bot does) is used at once
            requests.put(f"{CATALOG}/houses/house1/kitchen/thresholds", json={"t_min": 12}).raise_for_status()
            send("house1", "kitchen", "temperature", 13)
            time.sleep(1)
            assert hvac_state("house1", "kitchen") == "OFF", "13 is above the new t_min: no command expected"
            send("house1", "kitchen", "temperature", 11)
            wait_until(lambda: hvac_state("house1", "kitchen") == "ON", what="kitchen ON with new t_min")

            # 4. a room added at runtime: just launch its connector
            procs.append(start_connector("house1", "garage"))
            assert requests.get(f"{CATALOG}/houses/house1/garage/thresholds").json()["t_min"] == 19
            time.sleep(1)
            send("house1", "garage", "temperature", 30)  # random start-up reading may have turned it ON
            send("house1", "garage", "temperature", 10)
            wait_until(lambda: hvac_state("house1", "garage") == "ON", what="new garage ON")

            # 5. HVAC switched off by hand (a command on MQTT, like mosquitto_pub): the controller sees the new
            #    state and switches it on again; a bad command is ignored
            probe.publish("smarthome/house1/kitchen/hvac", {"command": "OFF"})
            wait_until(lambda: hvac_state("house1", "kitchen") == "OFF", what="kitchen OFF by hand")
            send("house1", "kitchen", "temperature", 5)
            wait_until(lambda: hvac_state("house1", "kitchen") == "ON", what="kitchen ON after manual OFF")
            probe.publish("smarthome/house1/kitchen/hvac", {"command": "HEAT"})
            time.sleep(0.5)
            assert hvac_state("house1", "kitchen") == "ON"
        finally:
            if probe:
                probe.stop()
            for p in reversed(procs):
                p.terminate()
                p.wait()
    print("e2e: all checks passed")


if __name__ == "__main__":
    main()
