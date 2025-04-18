from voice_utils import say

def handle_lighting(command):
    if "światło w salonie" in command and ("zapal" in command or "włącz" in command):
        say("Włączam światło w salonie.")
        # Tu będzie np. MQTT lub GPIO
    elif "światło w salonie" in command and "wyłącz" in command:
        say("Wyłączam światło w salonie.")
    else:
        return False  # Komenda nieobsługiwana
    return True
