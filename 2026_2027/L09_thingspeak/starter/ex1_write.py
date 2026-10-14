"""Ex1: write one value to field1 of a ThingSpeak channel.

Run:  python ex1_write.py 23.5
"""
import sys

import requests

from config import get_secret

UPDATE_URL = "https://api.thingspeak.com/update"

value = sys.argv[1] if len(sys.argv) > 1 else "23.5"
raise NotImplementedError("TODO Ex1: read THINGSPEAK_WRITE_KEY with get_secret; without key print the URL (key masked) and exit; otherwise requests.get(UPDATE_URL, params={api_key, field1}) and print the entry number ('0' = refused)")
