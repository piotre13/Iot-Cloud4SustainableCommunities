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
        # topic "smarthome/house1/kitchen/temperature" -> key "house1/kitchen/temperature" -> field number
        # HVAC state topic ends with /hvac/state: key "house1/kitchen/hvac", value 1 (ON) or 0 (OFF)
        # unknown key or missing value: ignore. Otherwise save in self.pending (use the lock)
        raise NotImplementedError("TODO Ex2: map the message to a field and store the latest value in self.pending")

    def upload(self):
        # take (and empty) self.pending under the lock; nothing pending -> return None
        # params = {"field1": value, ...}; no write_key -> print "[dry run] GET ..." and return params
        # else requests.get(UPDATE_URL, params={"api_key": ..., **params}); answer "0" = refused
        # on failure put the data back in self.pending (newer values win) and print the error
        raise NotImplementedError("TODO Ex2: send all pending fields in one update, re-queue on failure")


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
