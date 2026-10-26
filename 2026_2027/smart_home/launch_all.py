"""Start the whole smart home: catalog, controller, ThingSpeak adaptor, Telegram bot, one connector per room.

Run from smart_home/ (mosquitto must already be running on the broker in catalog/catalog.json):
    python launch_all.py

Each service writes its output to logs/<service>.log  (follow one with: tail -f logs/controller.log).
Ctrl+C stops everything. To add a room at runtime, from another terminal:
    python -m device_connector.service house2 kitchen
"""
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from common.config import catalog_url, get_secret

HERE = Path(__file__).parent
LOGS = HERE / "logs"

ROOMS = [  # house, room of each connector
    ("house1", "kitchen"),
    ("house1", "bedroom"),
    ("house2", "living_room"),
    ("house2", "bedroom"),
]


def start(name, *args):
    log = open(LOGS / f"{name}.log", "w")
    # -u: unbuffered, so the log files fill while the service runs
    proc = subprocess.Popen([sys.executable, "-u", "-m", *args], cwd=HERE, stdout=log, stderr=subprocess.STDOUT)
    print(f"started {name:<28} pid {proc.pid}")
    return proc


def wait_for_catalog(url, proc, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        if proc.poll() is not None:  # e.g. the port is still taken by a catalog from an earlier run
            raise RuntimeError("catalog exited, see logs/catalog.log")
        try:
            r = requests.get(f"{url}/broker", timeout=1)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            time.sleep(0.2)
    raise RuntimeError(f"catalog not reachable at {url}, see logs/catalog.log")


def wait_all(procs, seconds):
    end = time.time() + seconds
    while time.time() < end and any(p.poll() is None for p in procs):
        time.sleep(0.1)


def main():
    LOGS.mkdir(exist_ok=True)
    try:
        requests.get(catalog_url(), timeout=1)
        sys.exit(f"Something already answers at {catalog_url()}: stop the previous run first")
    except requests.RequestException:
        pass  # port free, good
    port = urlparse(catalog_url()).port
    procs = [start("catalog", "catalog.service", str(port))]
    try:
        broker = wait_for_catalog(catalog_url(), procs[0])
        print(f"catalog up, broker {broker['host']}:{broker['port']}")
        procs.append(start("controller", "controller.service"))
        procs.append(start("thingspeak_adaptor", "thingspeak_adaptor.service"))
        if get_secret("TELEGRAM_TOKEN"):
            procs.append(start("telegram_bot", "telegram_bot.service"))
        else:
            print("TELEGRAM_TOKEN missing in .env: bot not started")
        for house, room in ROOMS:
            procs.append(start(f"dc_{house}_{room}", "device_connector.service", house, room))
        print("all running, Ctrl+C to stop")
        while True:
            time.sleep(1)
            for p in list(procs):  # copy: we remove from it
                if p.poll() is not None:
                    print(f"pid {p.pid} exited with code {p.returncode}: check logs/")
                    procs.remove(p)
    except KeyboardInterrupt:
        pass
    finally:
        # Ctrl+C in the terminal already reached every service: give them time to clean up.
        # A second SIGINT would interrupt that clean-up, so only the ones still running get it.
        wait_all(procs, 3)
        for p in procs:
            if p.poll() is None:
                p.send_signal(signal.SIGINT)
        wait_all(procs, 5)
        for p in procs:
            if p.poll() is None:
                p.kill()
        print("stopped")


if __name__ == "__main__":
    main()
