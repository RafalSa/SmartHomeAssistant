import time
import intent_recognizer
import voice_utils
from logger_setup import get_logger

from modules import lighting
from modules import blinds
from modules import locks
from modules import heating
from modules import weather

logger = get_logger("MainApp")


def handle_command(text):
    if not text:
        return

    intent = intent_recognizer.recognize_intent(text)
    logger.info(f"Rozpoznana intencja z tekstu '{text}': {intent}")

    if intent == "turn_on_lights":
        lighting.living_room_light.turn_on()
    elif intent == "turn_off_lights":
        lighting.living_room_light.turn_off()
    elif intent == "open_blinds":
        blinds.main_blinds.open()
    elif intent == "close_blinds":
        blinds.main_blinds.close()
    elif intent == "open_locks":
        locks.front_door.open()
    elif intent == "close_locks":
        locks.front_door.close()
    elif intent == "set_temperature":
        heating.home_heater.set_temperature()
    elif intent == "check_weather":
        weather.get_current_weather()
    else:
        logger.warning(f"Nie powiązano komendy z żadną akcją: {text}")
        voice_utils.say("Nie rozumiem polecenia.")


if __name__ == "__main__":
    logger.info("=== Start systemu SmartHomeAssistant ===")
    print("\n--- Aplikacja uruchomiona w tle ---")
    print("Powiedz 'Witam dom', aby wybudzić asystenta.")

    voice_utils.say("System gotowy. Nasłuchuję w tle.")

    while True:
        # Faza 1: Ciche nasłuchiwanie słowa wybudzającego (Wake Word)
        wake_word_candidate = voice_utils.listen_for_input()

        if not wake_word_candidate:
            continue

        if "witam dom" in wake_word_candidate:
            logger.info("Wybudzono asystenta (Wake Word).")
            voice_utils.say("Słucham?")

            # Zapisujemy czas wybudzenia
            last_activity_time = time.time()
            active_timeout = 60  # Czas w sekundach (1 minuta)

            # Faza 2: Tryb aktywny (nasłuchuje komend przez określony czas)
            while True:
                command = voice_utils.listen_for_input()

                if command:
                    # Jeśli usłyszał komendę, resetujemy licznik czasu
                    last_activity_time = time.time()

                    # Komendy do całkowitego wyłączenia programu
                    if command in ["koniec", "exit", "stop", "wyłącz się", "zakończ"]:
                        logger.info("Zamykanie systemu przez komendę głosową.")
                        voice_utils.say("Zamykam system. Do widzenia.")
                        exit(0)  # Całkowicie kończy działanie programu

                    # Ręczne uśpienie asystenta
                    elif command in ["idź spać", "uśpij", "dobranoc", "dziękuję to wszystko"]:
                        logger.info("Ręczne uśpienie asystenta.")
                        voice_utils.say("Przechodzę w tryb uśpienia.")
                        break  # Przerywa tryb aktywny, wraca do Fazy 1

                    # Obsługa normalnych komend
                    handle_command(command)

                else:
                    # Jeśli w tej iteracji nic nie usłyszał, sprawdzamy, ile czasu minęło
                    elapsed_time = time.time() - last_activity_time
                    if elapsed_time > active_timeout:
                        logger.info("Brak aktywności przez 1 minutę. Automatyczne usypianie.")
                        voice_utils.say("Brak aktywności. Przechodzę w tryb uśpienia.")
                        break  # Przerywa tryb aktywny, wraca do Fazy 1