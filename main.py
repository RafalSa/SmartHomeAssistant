import intent_recognizer
import lighting
import blinds

def handle_command(text):
    intent = intent_recognizer.recognize_intent(text)

    if intent == "turn_on_lights":
        lighting.turn_on()
    elif intent == "turn_off_lights":
        lighting.turn_off()
    elif intent == "open_blinds":
        blinds.open()
    elif intent == "close_blinds":
        blinds.close()
    else:
        print("Nie rozumiem polecenia.")

# Przykład użycia:
if __name__ == "__main__":
    while True:
        cmd = input("Powiedz coś: ")
        if cmd.lower() in ["koniec", "exit", "stop"]:
            break
        handle_command(cmd)
