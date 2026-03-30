import requests
from voice_utils import say
from logger_setup import get_logger

logger = get_logger("WeatherAPI")


def get_current_weather():
    logger.info("Próba pobrania danych pogodowych dla Chorzowa...")
    url = "https://api.open-meteo.com/v1/forecast?latitude=50.30&longitude=18.95&current_weather=true"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        temp = data['current_weather']['temperature']
        logger.info(f"Pobrano temperaturę: {temp}°C")
        say(f"Obecna temperatura na zewnątrz to {temp} stopni Celsjusza.")
    except Exception as e:
        logger.error(f"Błąd połączenia z API pogodowym: {e}")
        say("Przepraszam, nie udało mi się połączyć z serwisem pogodowym.")