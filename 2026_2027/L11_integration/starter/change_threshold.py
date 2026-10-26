"""Change one threshold of a room through the catalog.

    python change_threshold.py house1 kitchen t_min 27
    python change_threshold.py house1 kitchen h_max 50 --catalog http://localhost:8080

The controller reads the thresholds from the catalog at every measurement: no restart needed.
Same thing with curl:
    curl -X PUT -H "Content-Type: application/json" -d '{"t_min": 27}' http://localhost:8080/houses/house1/kitchen/thresholds
"""
import argparse

import requests

parser = argparse.ArgumentParser(description="Change a room threshold in the catalog")
parser.add_argument("house_id")
parser.add_argument("room_id")
parser.add_argument("key", choices=["t_min", "t_max", "h_max"])
parser.add_argument("value", type=float)
parser.add_argument("--catalog", default="http://localhost:8080")
args = parser.parse_args()

# TODO Ex3: PUT {args.key: args.value} to {catalog}/houses/<house>/<room>/thresholds and print the result
raise NotImplementedError("TODO Ex3: change the threshold through the catalog")
