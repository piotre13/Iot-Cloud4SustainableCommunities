import random
import time

import requests

url = "http://localhost:8080/"
for i in range(5):
    body = {
        "room": "kitchen",
        "name": "sens%i" % i,
        "time_steps": random.randint(5, 100),
        "freq": random.randint(1, 5),
    }

    res = requests.post(url, json=body)
    time.sleep(2)
    print(res)
