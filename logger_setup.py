import logging


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Formatowanie: Data - Poziom - [Moduł] Wiadomość
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(message)s')

        # Zapisywanie do pliku smarthome.log
        fh = logging.FileHandler('smarthome.log', encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Wypisywanie w konsoli
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger