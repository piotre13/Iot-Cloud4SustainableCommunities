"""Offline check of the adaptor logic (no catalog, no broker, no internet).  Run: python check_adaptor.py"""
import thingspeak_adaptor as ts
from senml import senml_record

adaptor = ts.ThingSpeakAdaptor("http://unused")  # no key -> dry run
adaptor.fields = {"house1/kitchen/temperature": 1, "house1/kitchen/hvac": 3, "house1/bedroom/humidity": 5}
adaptor.notify("smarthome/house1/kitchen/temperature", senml_record("x", "x", "", 20.0))
adaptor.notify("smarthome/house1/kitchen/temperature", senml_record("x", "x", "", 21.5))  # only the latest is kept
adaptor.notify("smarthome/house1/bedroom/humidity", senml_record("x", "x", "", 55))
adaptor.notify("smarthome/house1/kitchen/hvac/state", {"state": "ON"})
adaptor.notify("smarthome/house2/bedroom/temperature", senml_record("x", "x", "", 30))  # not mapped: ignored
assert adaptor.upload() == {"field1": 21.5, "field3": 1, "field5": 55}
assert adaptor.upload() is None  # nothing new, nothing sent

# ThingSpeak refuses with "0": values must stay queued
ts.requests.get = lambda *a, **k: type("R", (), {"text": "0", "raise_for_status": lambda self: None})()
adaptor.write_key = "fake"
adaptor.notify("smarthome/house1/kitchen/temperature", senml_record("x", "x", "", 19.0))
adaptor.upload()
assert adaptor.pending == {1: 19.0}
print("all checks passed")
