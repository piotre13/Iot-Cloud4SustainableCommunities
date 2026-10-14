"""Add a whole house at runtime: one device connector (a separate process) per room.

    python add_house.py house3 kitchen bedroom --first-port 8085

No code of smart_home is touched: each connector registers itself in the catalog (POST /devices),
which creates the house and the rooms. Ctrl+C stops all the connectors.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

SMART_HOME = Path(__file__).resolve().parent.parent.parent / "smart_home"

parser = argparse.ArgumentParser(description="Start one device connector per room of a new house")
parser.add_argument("house_id")
parser.add_argument("rooms", nargs="+", help="room names")
parser.add_argument("--first-port", type=int, default=8085, help="REST port of the first room, then +1 each")
parser.add_argument("--interval", type=float, default=10, help="seconds between measurements")
args = parser.parse_args()

procs = []
# TODO Ex2: for each room start `python -u -m device_connector.service <house> <room> <port> --interval <n>`
# with subprocess.Popen (cwd=SMART_HOME, port = first_port + index) and append the process to procs
raise NotImplementedError("TODO Ex2: start one device connector per room")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass  # Ctrl+C in the terminal already reached the connectors too
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait()
    print("stopped")
