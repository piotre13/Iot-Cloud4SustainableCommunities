import random
import time

import requests

url = "http://localhost:8080/"
body = {
    "type": "light",
    "room": "living_room",
    "steps": random.randint(5, 100),
    "freq": 1,
}
for i in range(5):
    res = requests.post(url, json=body)
    print(res)
    time.sleep(3)
