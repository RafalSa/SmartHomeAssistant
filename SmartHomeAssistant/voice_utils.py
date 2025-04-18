import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()

def say(text):
    engine.say(text)
    engine.runAndWait()

def listen_for_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Czekam na odpowiedź...")
        audio = recognizer.listen(source)
        try:
            result = recognizer.recognize_google(audio, language='pl-PL')
            print("Rozpoznano:", result)
            return result.lower()
        except:
            say("Nie zrozumiałem.")
            return ""
