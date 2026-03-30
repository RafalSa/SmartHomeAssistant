import re
from modules.base_device import SmartDevice
from voice_utils import say, listen_for_input


class Thermostat(SmartDevice):
    def __init__(self, name="Ogrzewanie"):
        super().__init__(name)
        if 'temperature' not in self.state:
            self.state['temperature'] = 21

    def extract_temperature(self, text):
        match = re.search(r'\b(\d{1,2})\b', text)
        if match:
            return int(match.group(1))
        return None

    def set_temperature(self):
        current_temp = self.state['temperature']
        say(f"Obecna temperatura to {current_temp} stopni. Na jaką ustawić?")

        response = listen_for_input()
        temp = self.extract_temperature(response)

        if temp:
            self.state['temperature'] = temp
            self.save_state()
            say(f"Ustawiam temperaturę na {temp} stopni.")
        else:
            say("Nie usłyszałem temperatury. Anuluję zmianę.")


home_heater = Thermostat("Termostat główny")