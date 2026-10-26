"""End-to-end teacher test: mosquitto + catalog + controller + connectors, all as real processes.

Run from this folder:  python test_e2e.py
Ports: MQTT 1886, catalog 8130, connectors 8131-8133. The connectors publish only once
(--interval 3600); the test injects chosen measurements, so every threshold crossing is deterministic.
"""
import json
import queue
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

from mymqtt import MyMQTT
from senml import senml_record

MQTT_PORT = 1886
CATALOG_PORT = 8130
CATALOG = f"http://localhost:{CATALOG_PORT}"
SEED = Path(__file__).parent / "catalog.json"


class Collector:
    def __init__(self):
        self.messages = queue.Queue()

    def notify(self, topic, payload):
        self.messages.put((topic, payload))


def spawn(*args):
    return subprocess.Popen([sys.executable, *args], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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
    proc = spawn("device_connector.py", house, room, "--interval", "3600", "--catalog", CATALOG)
    wait_until(lambda: requests.get(f"{CATALOG}/devices/dc_{house}_{room}", timeout=1).ok, what=f"{house}/{room} registration")
    return proc


def main():
    procs = []
    with tempfile.TemporaryDirectory() as tmp:
        state = json.loads(SEED.read_text())
        state["broker"]["port"] = MQTT_PORT  # the catalog default stays 1883
        (Path(tmp) / "state.json").write_text(json.dumps(state))
        probe = None
        try:
            procs.append(subprocess.Popen(["/opt/homebrew/sbin/mosquitto", "-p", str(MQTT_PORT)],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            procs.append(spawn("catalog.py", str(CATALOG_PORT), str(Path(tmp) / "state.json")))
            wait_until(lambda: requests.get(f"{CATALOG}/broker", timeout=1).ok, what="catalog")
            procs.append(spawn("controller.py", "--catalog", CATALOG))
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
            send("house2", "bedroom", "temperature", 10)
            wait_until(lambda: hvac_state("house2", "bedroom") == "ON", what="house2 bedroom ON")

            # 2. humidity alert, sent once while it stays high
            send("house1", "kitchen", "humidity", 50)
            send("house1", "kitchen", "humidity", 90)
            topic, alert = collector.messages.get(timeout=3)
            assert topic == "smarthome/house1/alerts" and alert["room"] == "kitchen", alert
            send("house1", "kitchen", "humidity", 91)
            time.sleep(1)
            assert collector.messages.empty(), "second alert while still humid"

            # 3. a threshold changed in the catalog is used at once
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
            send("house1", "garage", "temperature", 30)
            time.sleep(0.5)  # let the state message come back before the next reading
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
