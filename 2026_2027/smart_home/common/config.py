import json
from pathlib import Path

import requests

SETTINGS_PATH = Path(__file__).parent.parent / "config" / "settings.json"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def catalog_url():
    return load_json(SETTINGS_PATH)["catalog_url"]


def get_broker(url):
    """Every service asks the catalog where the broker is: {"host": ..., "port": ...}."""
    r = requests.get(f"{url}/broker", timeout=5)
    r.raise_for_status()
    return r.json()
