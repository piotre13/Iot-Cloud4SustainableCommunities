import json
from pathlib import Path

import requests

SETTINGS_PATH = Path(__file__).parent / "settings.json"


def catalog_url():
    with open(SETTINGS_PATH, encoding="utf-8") as f:
        return json.load(f)["catalog_url"]


def get_broker(url):
    """Every service asks the catalog where the broker is: {"host": ..., "port": ...}."""
    r = requests.get(f"{url}/broker", timeout=5)
    r.raise_for_status()
    return r.json()
