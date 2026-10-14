# Ex2 - read the configuration file
import json
from pathlib import Path

# path relative to this script, so it works from any folder
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config(path):
    raise NotImplementedError("TODO Ex2: open the file and return json.load(f)")


def list_rooms(config):
    raise NotImplementedError("TODO Ex2: return strings like house1/kitchen")


def get_thresholds(config, house_id, room_id):
    raise NotImplementedError("TODO Ex2: return the thresholds dict of a room, or None if not found")


if __name__ == "__main__":
    config = load_config(CONFIG_PATH)
    print(list_rooms(config))
    print(get_thresholds(config, "house1", "kitchen"))
    print(get_thresholds(config, "house9", "garage"))  # None
