from modules.base_device import SmartDevice
from voice_utils import say

class Blind(SmartDevice):
    def __init__(self, name="Rolety"):
        super().__init__(name)
        if 'is_open' not in self.state:
            self.state['is_open'] = False

    def open(self):
        if self.state['is_open']:
            say(f"{self.name} są już otwarte.")
        else:
            self.state['is_open'] = True
            self.save_state()
            say(f"Otwieram {self.name}.")

    def close(self):
        if not self.state['is_open']:
            say(f"{self.name} są już zamknięte.")
        else:
            self.state['is_open'] = False
            self.save_state()
            say(f"Zamykam {self.name}.")

main_blinds = Blind("Rolety w salonie")