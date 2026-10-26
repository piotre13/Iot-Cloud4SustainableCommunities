# Ex2 - read the configuration file
import json
from pathlib import Path

# path relative to this script, so it works from any folder
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config(path):
    with open(path, "r") as f:
        config = json.load(f)
    return config


def list_rooms(config):
    list_rooms = []
    for house in config["houses"]:
        house_name = house["house_id"]
        for room in house["rooms"]:
            room_id = room["room_id"]

            full_name = house_name + "/" + room_id
            list_rooms.append(full_name)

    return list_rooms


def get_thresholds(config, house_id, room_id):
    for house in config["houses"]:
        if house["house_id"] == house_id:
            for room in house["rooms"]:
                if room["room_id"] == room_id:
                    return room["thresholds"]
    print("House or Room not found")


if __name__ == "__main__":
    config = load_config(CONFIG_PATH)
    print(list_rooms(config))
    print(get_thresholds(config, "house1", "kitchen"))
    print(get_thresholds(config, "house9", "garage"))  # None
