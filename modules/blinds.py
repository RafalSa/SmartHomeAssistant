import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice_utils import say

def handle_blinds(command):
    if "rolety w domu" in command and ("zwiń" in command or "daj w górę" in command):
        say("Zwijam wszystkie rolety.")
        # Tu będzie np. MQTT lub GPIO
    elif "rolety w domu" in command and ("rozwiń" in command or "daj w dół" in command):
        say("Rozwijam wszystkie rolety.")
    else:
        return False  # Komenda nieobsługiwana
    return True
