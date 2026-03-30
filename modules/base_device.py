import json
import os
from logger_setup import get_logger

logger = get_logger("BaseDevice")
STATE_FILE = "device_states.json"


class SmartDevice:
    def __init__(self, name):
        self.name = name
        self.state = {}
        self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if self.name in data:
                        self.state = data[self.name]
                        logger.info(f"Wczytano stan z pamięci dla {self.name}: {self.state}")
            except Exception as e:
                logger.error(f"Błąd wczytywania stanu: {e}")

    def save_state(self):
        data = {}
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        data[self.name] = self.state
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Zapisano nowy stan dla {self.name}")