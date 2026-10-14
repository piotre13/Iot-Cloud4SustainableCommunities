# Ex3 - change a threshold and save to a NEW file
import json
from pathlib import Path

from ex2_config import CONFIG_PATH, load_config, get_thresholds

NEW_PATH = Path(__file__).parent / "config_modified.json"


def save_config(config, path):
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    config = load_config(CONFIG_PATH)
    thresholds = get_thresholds(config, "house1", "kitchen")
    thresholds["t_max"] = 25  # the dict is mutable: this changes config too
    save_config(config, NEW_PATH)
    print("Saved", NEW_PATH.name)
    print(load_config(NEW_PATH)["houses"][0]["rooms"][0])
