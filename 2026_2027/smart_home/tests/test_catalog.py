"""Catalog CRUD test. Run from smart_home/:  python -m tests.test_catalog

Starts the catalog on a spare port with a temporary state file, so the real catalog_state.json is untouched.
"""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

PORT = 8099
URL = f"http://localhost:{PORT}"


def start_catalog(state_path):
    proc = subprocess.Popen([sys.executable, "-m", "catalog.service", str(PORT), str(state_path)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            requests.get(f"{URL}/broker", timeout=0.2)
            return proc
        except requests.ConnectionError:
            time.sleep(0.1)
    proc.kill()
    raise RuntimeError("catalog did not start")


def check():
    # read
    assert requests.get(f"{URL}/broker").json() == {"host": "localhost", "port": 1883}
    houses = requests.get(f"{URL}/houses").json()
    assert [h["house_id"] for h in houses] == ["house1", "house2"]
    assert requests.get(f"{URL}/houses/house1/kitchen/thresholds").json()["t_max"] == 23

    # thresholds update (what the bot does)
    r = requests.put(f"{URL}/houses/house1/kitchen/thresholds", json={"t_max": 25})
    assert r.status_code == 200 and r.json()["t_max"] == 25 and r.json()["t_min"] == 19
    assert requests.put(f"{URL}/houses/house1/kitchen/thresholds", json={"t_max": "hot"}).status_code == 400
    assert requests.put(f"{URL}/houses/house1/kitchen/thresholds", json={"color": 1}).status_code == 400
    nan = '{"t_min": NaN}'  # json.loads accepts NaN/Infinity: the catalog must refuse them
    assert requests.put(f"{URL}/houses/house1/kitchen/thresholds", data=nan).status_code == 400
    assert requests.put(f"{URL}/houses/house1/kitchen/thresholds", data='{"t_max": Infinity}').status_code == 400
    assert requests.put(f"{URL}/houses/house1/kitchen/thresholds", json={"t_min": 30}).status_code == 400
    assert requests.get(f"{URL}/houses/house1/kitchen/thresholds").json()["t_min"] == 19

    # device registration is an upsert and creates a new room with default thresholds
    dc = {"device_id": "dc_garage", "house_id": "house1", "room_id": "garage",
          "sensors": ["temperature"]}
    r = requests.post(f"{URL}/devices", json=dc)
    assert r.status_code == 201
    # the answer is the configuration of the device: broker, base topic, default publish interval
    assert r.json() == {"device": dc, "broker": {"host": "localhost", "port": 1883},
                        "base_topic": "smarthome/house1/garage", "interval": 10}, r.json()
    assert requests.post(f"{URL}/devices", json={**dc, "sensors": ["temperature", "humidity"]}).status_code == 201
    devices = requests.get(f"{URL}/devices").json()
    assert len(devices) == 1 and devices[0]["sensors"] == ["temperature", "humidity"]
    assert requests.get(f"{URL}/devices/dc_garage").json()["room_id"] == "garage"
    assert requests.get(f"{URL}/houses/house1/garage/thresholds").json() == {"t_min": 19, "t_max": 23, "h_max": 70}
    # a brand new house too
    assert requests.post(f"{URL}/devices", json={**dc, "device_id": "dc_h3", "house_id": "house3"}).status_code == 201
    assert requests.get(f"{URL}/houses/house3").json()["rooms"][0]["room_id"] == "garage"

    # houses, users, thingspeak
    assert requests.post(f"{URL}/houses", json={"house_id": "house4", "rooms": []}).status_code == 201
    assert requests.post(f"{URL}/users", json={"chat_id": 1, "name": "Ada", "houses": ["house1"]}).status_code == 201
    assert requests.get(f"{URL}/users").json()[0]["name"] == "Ada"
    ts = {"channel_id": 42, "fields": {"house1/kitchen/temperature": 1}}
    assert requests.put(f"{URL}/thingspeak", json=ts).json() == ts

    # errors
    assert requests.get(f"{URL}/houses/nope").status_code == 404
    assert requests.get(f"{URL}/houses/house1/nope/thresholds").status_code == 404
    assert requests.get(f"{URL}/devices/nope").status_code == 404
    assert requests.get(f"{URL}/nope").status_code == 404
    assert requests.post(f"{URL}/devices", json={"device_id": "x"}).status_code == 400
    assert requests.post(f"{URL}/devices", data="not json").status_code == 400


def main():
    with tempfile.TemporaryDirectory() as tmp:
        state = Path(tmp) / "catalog_state.json"
        proc = start_catalog(state)
        try:
            check()
        finally:
            proc.terminate()
            proc.wait()
        # persistence: a restarted catalog still knows the registered device
        proc = start_catalog(state)
        try:
            assert requests.get(f"{URL}/devices/dc_garage").status_code == 200
            assert requests.get(f"{URL}/houses/house1/kitchen/thresholds").json()["t_max"] == 25
        finally:
            proc.terminate()
            proc.wait()
    print("catalog: all checks passed")


if __name__ == "__main__":
    main()
