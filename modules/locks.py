from modules.base_device import SmartDevice
from voice_utils import say

class Lock(SmartDevice):
    def __init__(self, name="Zamek główny"):
        super().__init__(name)
        if 'is_locked' not in self.state:
            self.state['is_locked'] = True

    def open(self):
        if not self.state['is_locked']:
            say(f"{self.name} jest już otwarty.")
        else:
            self.state['is_locked'] = False
            self.save_state()
            say(f"Otwieram {self.name}.")

    def close(self):
        if self.state['is_locked']:
            say(f"{self.name} jest już zamknięty.")
        else:
            self.state['is_locked'] = True
            self.save_state()
            say(f"Zamykam {self.name}.")

front_door = Lock("Drzwi wejściowe")