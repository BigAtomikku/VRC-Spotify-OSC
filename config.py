import json

CONFIG_PATH = "config.json"


def save(config_data):
    with open(CONFIG_PATH, 'w') as file:
        json.dump(config_data, file, indent=4)


def create_default_config():
    default_config = {
        "client_id": "",
        "ip": "127.0.0.1",
        "port": 9000
    }
    save(default_config)
    return default_config


def _load_config():
    try:
        with open(CONFIG_PATH, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return create_default_config()


class ConfigManager:
    def __init__(self):
        self.config = _load_config()

    def get(self, key, default=None):
        return self.config.get(key, default)

    def update(self, updates):
        self.config.update(updates)
        save(self.config)
