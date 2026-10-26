"""Small client of the catalog: what any other service (controller, bot, ...) will do.

Usage: python catalog_client.py [catalog_url]
"""
import sys

import requests

catalog = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

# 1. list houses and rooms
for house in requests.get(f"{catalog}/houses", timeout=5).json():
    print(house["house_id"], [room["room_id"] for room in house["rooms"]])

# 2. read the thresholds of one room
url = f"{catalog}/houses/house1/kitchen/thresholds"
print("before:", requests.get(url, timeout=5).json())

# 3. change one threshold (partial PUT)
response = requests.put(url, json={"t_max": 25}, timeout=5)
print("after: ", response.status_code, response.json())

# 4. an invalid change is refused with 400
response = requests.put(url, json={"t_min": 40}, timeout=5)
print("t_min=40:", response.status_code)

# 5. list the registered devices
for device in requests.get(f"{catalog}/devices", timeout=5).json():
    print(device["device_id"], device["sensors"])
