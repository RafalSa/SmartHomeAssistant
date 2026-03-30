import speech_recognition as sr

# Lista najbardziej prawdopodobnych ID z Twojego poprzedniego logu
potencjalne_id = [1, 2, 13, 14, 33, 35]
recognizer = sr.Recognizer()

print("=== TEST AKTYWNOŚCI MIKROFONÓW ===")
print("Będę testował kolejne wejścia. Gdy zobaczysz komunikat 'MÓW TERAZ', powiedz coś głośno!\n")

for i in potencjalne_id:
    print(f"--- Testuję ID {i} ---")
    try:
        with sr.Microphone(device_index=i) as source:
            print("MÓW TERAZ (masz 3 sekundy)...")
            # Krótka kalibracja
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # Nasłuchiwanie z krótkim limitem
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                print(f">>> SUKCES! ID {i} faktycznie rejestruje dźwięk! <<<")
            except sr.WaitTimeoutError:
                print(f"Porażka: ID {i} nagrywa tylko ciszę.")
    except Exception as e:
        print(f"Błąd przy otwieraniu ID {i}: {e}")
    print("-" * 25)