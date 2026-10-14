import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

SETTINGS_PATH = Path(__file__).parent / "settings.json"
ENV_PATH = Path(__file__).parent.parent.parent / ".env"  # 2026_2027/.env, never committed


def catalog_url():
    with open(SETTINGS_PATH, encoding="utf-8") as f:
        return json.load(f)["catalog_url"]


def get_broker(url):
    """Every service asks the catalog where the broker is: {"host": ..., "port": ...}."""
    r = requests.get(f"{url}/broker", timeout=5)
    r.raise_for_status()
    return r.json()


def get_secret(name):
    """Read a secret (token, API key) from 2026_2027/.env or the environment. None if missing."""
    load_dotenv(ENV_PATH)
    return os.getenv(name) or None
