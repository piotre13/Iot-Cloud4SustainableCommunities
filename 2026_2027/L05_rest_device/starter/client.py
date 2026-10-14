"""Ex2 - client of the device connector(s).

Usage: python client.py http://localhost:8081 [http://localhost:8082 ...]
Reads every room and switches the HVAC ON if the room is colder than 19 Cel, OFF otherwise (heating).
"""
import sys

import requests

urls = sys.argv[1:]
if not urls:
    sys.exit("Usage: python client.py <base_url> [<base_url> ...]")

raise NotImplementedError("TODO Ex2: for each url: GET the room, print it, PUT /hvac ON if temperature < 19 else OFF, print the status code")
