import json
import os


def load_json(filename: str):
    filename: str = f"{filename}.json"
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return None


def save_json(json_data: dict, filename: str):
    with open(f"{filename}.json", "w") as f:
        return json.dump(json_data, f)
