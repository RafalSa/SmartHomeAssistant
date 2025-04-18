import speech_recognition as sr
import pyttsx3

# Inicjalizacja silnika mowy
engine = pyttsx3.init()

def say(text):
    engine.say(text)
    engine.runAndWait()

def listen_for_input():
    recognizer = sr.Recognizer()

    # Ustawienia mikrofonu
    recognizer.energy_threshold = 4000  # Zwiększenie progu czułości
    recognizer.dynamic_energy_threshold = True  # Dynamiczna zmiana czułości

    with sr.Microphone() as source:
        print("Czekam na odpowiedź...")

        # Redukcja szumów tła
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            # Słuchanie w sposób asynchroniczny
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

            # Rozpoznawanie mowy z Google
            result = recognizer.recognize_google(audio, language='pl-PL')
            print("Rozpoznano:", result)
            return result.lower()

        except sr.UnknownValueError:
            # W przypadku, gdy Google nie rozpozna mowy
            say("Nie zrozumiałem, spróbuj ponownie.")
            return ""
        except sr.RequestError:
            # W przypadku błędów związanych z siecią
            say("Błąd połączenia z serwisem rozpoznawania mowy.")
            return ""
        except Exception as e:
            # Obsługa innych błędów
            say(f"Wystąpił błąd: {str(e)}")
            return ""

# Testowanie funkcji
say("Proszę podać komendę")
listen_for_input()
