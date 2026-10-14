# Ex2 - read the configuration file
import json
from pathlib import Path

# path relative to this script, so it works from any folder
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config(path):
    with open(path) as f:
        return json.load(f)


def list_rooms(config):
    rooms = []
    for house in config["houses"]:
        for room in house["rooms"]:
            rooms.append(house["house_id"] + "/" + room["room_id"])
    return rooms


def get_thresholds(config, house_id, room_id):
    for house in config["houses"]:
        if house["house_id"] == house_id:
            for room in house["rooms"]:
                if room["room_id"] == room_id:
                    return room["thresholds"]
    return None


if __name__ == "__main__":
    config = load_config(CONFIG_PATH)
    print(list_rooms(config))
    print(get_thresholds(config, "house1", "kitchen"))
    print(get_thresholds(config, "house9", "garage"))  # None
