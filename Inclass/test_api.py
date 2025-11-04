import json

import requests

r = requests.get(
    "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m"
)

print(json.dumps(r.json(), indent=2))
