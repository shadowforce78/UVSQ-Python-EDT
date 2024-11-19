
import json
import os

CONFIG_FILE = "user_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {"class": "INF1-b2", "dark_mode": False}

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)