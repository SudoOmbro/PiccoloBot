import json


def load_json(filename: str):
    with open(f"{filename}.json", "r") as f:
        return json.load(f)


def save_json(json_data: dict, filename: str):
    with open(f"{filename}.json", "w") as f:
        return json.dump(json_data, f)
