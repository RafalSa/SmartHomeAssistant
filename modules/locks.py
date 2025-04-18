import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice_utils import say

def handle_locks(command):
    if "Zamki w domu" in command and ("otwórz" in command or "otwórz drzwi" in command):
        say("Otwieram twoj dom.")
        # Tu będzie np. MQTT lub GPIO
    elif "Zamki w domu" in command and ("zamknij" in command or "zamknij drzwi" in command):
        say("Zamykam twoj dom.")
    else:
        return False  # Komenda nieobsługiwana
    return True
