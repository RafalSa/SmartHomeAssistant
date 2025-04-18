import speech_recognition as sr
from voice_utils import say

def listen_for_input():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Czekam na odpowiedź...")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            result = recognizer.recognize_google(audio, language='pl-PL')
            print("Rozpoznano:", result)
            return result.lower()
        except sr.UnknownValueError:
            say("Nie zrozumiałem, spróbuj ponownie.")
            return ""
        except sr.RequestError:
            say("Błąd połączenia z serwisem rozpoznawania mowy.")
            return ""
        except Exception as e:
            say(f"Wystąpił błąd: {str(e)}")
            return ""

def handle_locks(command):
    if "zamki w domu" in command and ("otwórz" in command or "otwórz drzwi" in command):
        say("Otwieram twój dom.")
    elif "zamki w domu" in command and ("zamknij" in command or "zamknij drzwi" in command):
        say("Zamykam twój dom.")
    else:
        return False  # Komenda nieobsługiwana
    return True
