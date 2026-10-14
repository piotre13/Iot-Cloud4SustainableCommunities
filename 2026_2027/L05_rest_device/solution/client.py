"""Ex2 - client of the device connector(s).

Usage: python client.py http://localhost:8081 [http://localhost:8082 ...]
Reads every room and switches the HVAC ON if the room is colder than 19 Cel, OFF otherwise (heating).
"""
import sys

import requests

urls = sys.argv[1:]
if not urls:
    sys.exit("Usage: python client.py <base_url> [<base_url> ...]")

for url in urls:
    room = requests.get(url).json()
    print(f"{room['house_id']}/{room['room_id']}: {room['measurements']} HVAC {room['hvac']}")

    command = "ON" if room["measurements"]["temperature"] < 19 else "OFF"
    r = requests.put(f"{url}/hvac", json={"command": command})
    print(f"  PUT /hvac {command} -> {r.status_code} {r.json()}")
