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

    # device registration: POST creates (409 if it exists), GET gives the same answer again
    garage = {"house_id": "house1", "room_id": "garage", "type": "device_connector",
              "sensors": ["temperature"], "actuators": ["hvac"]}
    assert requests.post(f"{URL}/devices", json={k: v for k, v in garage.items() if k != "actuators"}).status_code == 400
    assert requests.post(f"{URL}/devices", json={**garage, "sensors": "temperature"}).status_code == 400
    assert requests.get(f"{URL}/devices").json() == []  # a refused registration stores nothing
    r = requests.post(f"{URL}/devices", json=garage)
    assert r.status_code == 201
    # the answer is the configuration of the device: broker, base topic, default publish interval
    config = {"device": garage, "broker": {"host": "localhost", "port": 1883},
              "base_topic": "smarthome/house1/garage", "interval": 10}
    assert r.json() == config, r.json()
    dev = f"{URL}/devices/house1/garage/device_connector"
    # a restart: the POST is refused (nothing replaced) and the same answer is read with a GET
    assert requests.post(f"{URL}/devices", json={**garage, "sensors": ["humidity"]}).status_code == 409
    assert requests.get(dev).json() == config
    assert requests.get(f"{URL}/devices").json() == [garage]
    assert requests.get(f"{URL}/houses/house1/garage/thresholds").json() == {"t_min": 19, "t_max": 23, "h_max": 70}
    # a brand new house too
    assert requests.post(f"{URL}/devices", json={**garage, "house_id": "house3"}).status_code == 201
    assert requests.get(f"{URL}/houses/house3").json()["rooms"][0]["room_id"] == "garage"

    # houses and rooms: POST creates, never replaces
    assert requests.post(f"{URL}/houses", json={"house_id": "house4"}).status_code == 201
    assert requests.post(f"{URL}/houses", json={"house_id": "house4"}).status_code == 409
    assert requests.post(f"{URL}/houses", json={"house_id": "house1"}).status_code == 409
    assert len(requests.get(f"{URL}/houses/house1").json()["rooms"]) == 3  # kitchen, bedroom, garage: untouched
    r = requests.post(f"{URL}/houses/house4/rooms", json={"room_id": "attic"})
    assert r.status_code == 201 and r.json()["thresholds"] == {"t_min": 19, "t_max": 23, "h_max": 70}
    assert requests.post(f"{URL}/houses/house4/rooms", json={"room_id": "attic"}).status_code == 409
    assert requests.post(f"{URL}/houses/nope/rooms", json={"room_id": "attic"}).status_code == 404

    # users: POST creates (409 if it exists), PUT updates
    ada = {"chat_id": 1, "name": "Ada", "houses": ["house1"]}
    assert requests.post(f"{URL}/users", json=ada).status_code == 201
    assert requests.post(f"{URL}/users", json={**ada, "name": "Other"}).status_code == 409
    assert requests.get(f"{URL}/users").json() == [ada]
    r = requests.put(f"{URL}/users/1", json={"name": "Ada L.", "houses": ["house1", "house2"]})
    assert r.status_code == 200 and r.json() == {"chat_id": 1, "name": "Ada L.", "houses": ["house1", "house2"]}
    assert requests.put(f"{URL}/users/99", json={"name": "x", "houses": []}).status_code == 404
    assert requests.put(f"{URL}/users/1", json={"name": "x"}).status_code == 400

    # thingspeak
    ts = {"channel_id": 42, "fields": {"house1/kitchen/temperature": 1}}
    assert requests.put(f"{URL}/thingspeak", json=ts).json() == ts

    # errors
    assert requests.get(f"{URL}/houses/nope").status_code == 404
    assert requests.get(f"{URL}/houses/house1/nope/thresholds").status_code == 404
    assert requests.get(f"{URL}/devices/house1/nope/device_connector").status_code == 404
    assert requests.get(f"{URL}/nope").status_code == 404
    assert requests.post(f"{URL}/houses", json={"rooms": []}).status_code == 400
    assert requests.post(f"{URL}/houses", data="not json").status_code == 400


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
            assert requests.get(f"{URL}/devices/house1/garage/device_connector").status_code == 200
            assert requests.get(f"{URL}/houses/house1/kitchen/thresholds").json()["t_max"] == 25
        finally:
            proc.terminate()
            proc.wait()
    print("catalog: all checks passed")


if __name__ == "__main__":
    main()
