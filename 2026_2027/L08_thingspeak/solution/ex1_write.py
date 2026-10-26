"""Ex1: write one value to field1 of a ThingSpeak channel.

Run:  python ex1_write.py 23.5
"""
import sys

import requests

from config import get_secret

UPDATE_URL = "https://api.thingspeak.com/update"

value = sys.argv[1] if len(sys.argv) > 1 else "23.5"
key = get_secret("THINGSPEAK_WRITE_KEY")
params = {"api_key": key, "field1": value}

if key is None:
    params["api_key"] = "***"  # never print a key
    print(f"No THINGSPEAK_WRITE_KEY in .env. I would call: GET {UPDATE_URL} {params}")
    sys.exit()

r = requests.get(UPDATE_URL, params=params, timeout=10)
# the answer is the entry number, or "0" if ThingSpeak refused the update
if r.text.strip() == "0":
    print("Refused (too frequent? wrong key?)")
else:
    print(f"Stored as entry {r.text}")
