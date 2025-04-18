import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice_utils import say, listen_for_input
import re

def extract_temperature(text):
    """Próbuje znaleźć liczbę w podanym tekście."""
    match = re.search(r'\b(\d{1,2})\b', text)
    if match:
        return int(match.group(1))
    return None

def handle_heating(command):
    if "temperatur" in command:
        if "podgrzej" in command or "cieplej" in command or "zwiększ temperaturę" in command:
            say("Na jaką temperaturę mam ustawić?")
            response = listen_for_input()
            temp = extract_temperature(response)
            if temp:
                say(f"Ustaw temperaturę na {temp} stopni.")
                # Tu wstaw logikę np. MQTT, np.: mqtt_client.publish("smarthome/heating/set", temp)
            else:
                say("Nie rozpoznałem temperatury.")
            return True

        elif "schłodź" in command or "zmniejsz ogrzewanie" in command:
            say("Na jaką temperaturę mam ustawić?")
            response = listen_for_input()
            temp = extract_temperature(response)
            if temp:
                say(f"Ustaw temperaturę na {temp} stopni.")
                # Logika do ustawiania niższej temp
            else:
                say("Nie rozpoznałem temperatury.")
            return True

    return False
