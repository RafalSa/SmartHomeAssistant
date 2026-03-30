import speech_recognition as sr
import pyttsx3

# Inicjalizacja silnika mowy
engine = pyttsx3.init()


def say(text):
    engine.say(text)
    engine.runAndWait()


def listen_for_input():
    recognizer = sr.Recognizer()

    # Próg czułości dostosowany do domowych warunków
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    # Używamy sprawdzonego, fizycznego wejścia mikrofonu
    with sr.Microphone(device_index=2) as source:
        print("Czekam na odpowiedź (mów teraz)...")

        # Szybka kalibracja tła
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            # Słuchamy z rozsądnymi limitami czasu
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            result = recognizer.recognize_google(audio, language='pl-PL')
            print(f"Rozpoznano: {result}")
            return result.lower()

        except sr.WaitTimeoutError:

            return ""
        except sr.UnknownValueError:
            print("Nie zrozumiałem, spróbuj ponownie.")
            return ""
        except sr.RequestError:
            print("Błąd połączenia z internetem (Google wymaga sieci).")
            return ""
        except Exception as e:
            print(f"Wystąpił błąd: {str(e)}")
            return ""


if __name__ == "__main__":
    say("Proszę podać komendę")
    listen_for_input()