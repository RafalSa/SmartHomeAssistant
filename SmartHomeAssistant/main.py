import speech_recognition as sr
from voice_utils import say
from modules.lighting import handle_lighting
from modules.blinds import handle_blinds
from modules.locks import handle_locks
from modules.heating import handle_heating

def recognize_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Słucham...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio, language='pl-PL').lower()
        except:
            say("Nie zrozumiałem, powtórz proszę.")
            return ""

while True:
    command = recognize_command()
    if not command:
        continue

    handled = (
        handle_lighting(command) or
        handle_blinds(command) or
        handle_locks(command) or
        handle_heating(command)
    )

    if not handled:
        say("Nie rozpoznano komendy.")
