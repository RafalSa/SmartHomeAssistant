import speech_recognition as sr
import pyttsx3
import threading
import queue

# Profesjonalna kolejka FIFO (First-In, First-Out) bezpieczna dla wątków
speech_queue = queue.Queue()


def _speak_worker():
    """Dedykowany wątek roboczy do obsługi syntezatora mowy."""
    engine = pyttsx3.init()

    while True:
        text = speech_queue.get()
        if text is None:
            break

        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Błąd syntezatora mowy: {e}")
        finally:
            speech_queue.task_done()


# Uruchamiamy naszego "pracownika" w tle
speaker_thread = threading.Thread(target=_speak_worker, daemon=True)
speaker_thread.start()


def say(text):
    """Wrzuć tekst do kolejki bez blokowania GUI"""
    speech_queue.put(text)


def listen_for_input():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone(device_index=2) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            result = recognizer.recognize_google(audio, language='pl-PL')
            return result.lower()

        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            print("Błąd połączenia z internetem.")
            return ""
        except Exception as e:
            print(f"Wystąpił błąd mikrofonu: {str(e)}")
            return ""