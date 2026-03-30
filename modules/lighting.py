from modules.base_device import SmartDevice
from voice_utils import say

class Light(SmartDevice):
    def __init__(self, name="Oświetlenie domowe"):
        super().__init__(name)
        # Ustawiamy stan domyślny tylko, jeśli nie wczytało niczego z JSONa
        if 'is_on' not in self.state:
            self.state['is_on'] = False

    def turn_on(self):
        if self.state['is_on']:
            say(f"{self.name} jest już włączone.")
        else:
            self.state['is_on'] = True
            self.save_state()
            say(f"Włączam {self.name}.")

    def turn_off(self):
        if not self.state['is_on']:
            say(f"{self.name} jest już wyłączone.")
        else:
            self.state['is_on'] = False
            self.save_state()
            say(f"Wyłączam {self.name}.")

living_room_light = Light("Światło w salonie")