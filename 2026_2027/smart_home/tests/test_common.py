"""common/ test: SenML, get_broker, MyMQTT round trip and re-subscribe after a broker restart.

Run from smart_home/:  python -m tests.test_common
Needs mosquitto (default path: Homebrew on Apple Silicon; override with MOSQUITTO=/path/to/mosquitto).
"""
import os
import queue
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from common.config import get_broker
from common.mymqtt import MyMQTT
from common.senml import senml_record
from tests.test_catalog import URL, start_catalog

MQTT_PORT = 1884
MOSQUITTO = os.environ.get("MOSQUITTO") or shutil.which("mosquitto") or "/opt/homebrew/sbin/mosquitto"


class Collector:
    def __init__(self):
        self.messages = queue.Queue()

    def notify(self, topic, payload):
        self.messages.put((topic, payload))


def start_broker():
    proc = subprocess.Popen([MOSQUITTO, "-p", str(MQTT_PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    return proc


def main():
    rec = senml_record("house1/kitchen", "temperature", "Cel", 21.4)
    assert set(rec) == {"bn", "n", "u", "t", "v"} and rec["v"] == 21.4

    with tempfile.TemporaryDirectory() as tmp:
        catalog = start_catalog(Path(tmp) / "state.json")
        try:
            assert get_broker(URL) == {"host": "localhost", "port": 1883}
        finally:
            catalog.terminate()
            catalog.wait()

    broker = start_broker()
    collector = Collector()
    sub = MyMQTT("test_sub", "localhost", MQTT_PORT, notifier=collector)
    pub = MyMQTT("test_pub", "localhost", MQTT_PORT)
    try:
        sub.start()
        pub.start()
        sub.subscribe("smarthome/+/+/temperature")
        time.sleep(0.5)
        pub.publish("smarthome/house1/kitchen/temperature", rec)
        pub.publish("smarthome/house1/kitchen/humidity", rec)  # not subscribed: must not arrive
        topic, payload = collector.messages.get(timeout=3)
        assert topic == "smarthome/house1/kitchen/temperature" and payload == rec
        time.sleep(0.5)
        assert collector.messages.empty()

        # broker restart: paho reconnects by itself, MyMQTT subscribes again in on_connect
        broker.terminate()
        broker.wait()
        broker = start_broker()
        time.sleep(3)
        pub.publish("smarthome/house2/bedroom/temperature", {"v": 1})
        topic, payload = collector.messages.get(timeout=5)
        assert topic == "smarthome/house2/bedroom/temperature"
    finally:
        sub.stop()
        pub.stop()
        broker.terminate()
        broker.wait()
    print("common: all checks passed")


if __name__ == "__main__":
    main()
