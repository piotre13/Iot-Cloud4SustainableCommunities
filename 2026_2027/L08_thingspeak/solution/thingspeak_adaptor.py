"""ThingSpeak adaptor: MQTT -> REST bridge towards a third-party cloud service.

Run:   python thingspeak_adaptor.py [--dry-run] [--catalog URL]

- Subscribes to every measurement and HVAC state.
- The catalog says which topic goes to which channel field (GET /thingspeak), e.g.
  {"channel_id": 0, "fields": {"house1/kitchen/temperature": 1, "house1/kitchen/hvac": 3}}.
  Rooms without a field are ignored (a free channel has 8 fields).
- A channel accepts one update every 15 s: the adaptor keeps the latest value of each field
  and sends them all together, once per interval. HVAC state is sent as 1 (ON) / 0 (OFF).
- The write key comes from 2026_2027/.env (THINGSPEAK_WRITE_KEY). Without it: dry run.
"""
import argparse
import threading
import time

import requests

from config import catalog_url, get_broker, get_secret
from mymqtt import MyMQTT

UPDATE_URL = "https://api.thingspeak.com/update"
MIN_INTERVAL = 15  # seconds, ThingSpeak free plan


class ThingSpeakAdaptor:
    def __init__(self, catalog, write_key=None):
        self.catalog = catalog
        self.write_key = write_key  # None = dry run
        self.fields = {}  # "house/room/kind" -> field number
        self.pending = {}  # field number -> latest value
        self.lock = threading.Lock()  # notify() runs in the MQTT thread, upload() in the main one
        self.mqtt = None

    def refresh_fields(self):
        r = requests.get(f"{self.catalog}/thingspeak", timeout=5)
        r.raise_for_status()
        self.fields = r.json()["fields"]

    def notify(self, topic, payload):
        parts = topic.split("/")
        if topic.endswith("/hvac/state"):
            key, value = f"{parts[1]}/{parts[2]}/hvac", 1 if payload.get("state") == "ON" else 0
        else:
            key, value = f"{parts[1]}/{parts[2]}/{parts[3]}", payload["e"][0].get("v")  # SenML
        field = self.fields.get(key)
        if field is None or value is None:
            return  # room not mapped to the channel
        with self.lock:
            self.pending[field] = value

    def upload(self):
        with self.lock:
            data, self.pending = self.pending, {}
        if not data:
            return None
        params = {f"field{field}": value for field, value in sorted(data.items())}
        if self.write_key is None:
            print(f"[dry run] GET {UPDATE_URL} {params}")
            return params
        try:
            r = requests.get(UPDATE_URL, params={"api_key": self.write_key, **params}, timeout=10)
            r.raise_for_status()
            # ThingSpeak answers the entry number, or "0" when the update is refused (e.g. too frequent)
            if r.text.strip() == "0":
                raise ValueError("update refused")
            print(f"ThingSpeak entry {r.text}: {params}")
        except (requests.RequestException, ValueError) as e:
            print(f"ThingSpeak update failed, retrying next time: {e}")
            with self.lock:
                self.pending = {**data, **self.pending}  # keep newer values that arrived meanwhile
        return params


def main():
    parser = argparse.ArgumentParser(description="MQTT -> ThingSpeak bridge")
    parser.add_argument("--dry-run", action="store_true", help="print the updates instead of sending them")
    parser.add_argument("--catalog", default=None, help="catalog URL (default: settings.json)")
    args = parser.parse_args()
    catalog = args.catalog or catalog_url()

    write_key = None if args.dry_run else get_secret("THINGSPEAK_WRITE_KEY")
    if write_key is None:
        print("No THINGSPEAK_WRITE_KEY (or --dry-run): printing updates instead of sending them")

    adaptor = ThingSpeakAdaptor(catalog, write_key)
    adaptor.refresh_fields()
    broker = get_broker(catalog)
    adaptor.mqtt = MyMQTT("thingspeak_adaptor", broker["host"], broker["port"], notifier=adaptor)
    adaptor.mqtt.start()
    for topic in ("smarthome/+/+/temperature", "smarthome/+/+/humidity", "smarthome/+/+/hvac/state"):
        adaptor.mqtt.subscribe(topic)
    try:
        while True:
            time.sleep(MIN_INTERVAL)
            try:
                adaptor.refresh_fields()  # a new mapping in the catalog is used without a restart
            except requests.RequestException as e:
                print(f"Catalog unreachable, keeping the old field map: {e}")
            adaptor.upload()
    except KeyboardInterrupt:
        adaptor.mqtt.stop()


if __name__ == "__main__":
    main()
