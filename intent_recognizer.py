import spacy

nlp = spacy.load("pl_core_news_md")

intents = {
    "turn_on_lights": ["włącz światło", "zapal lampę", "potrzebuję światła", "oświetlenie on"],
    "turn_off_lights": ["zgaś światło", "ciemność", "wyłącz oświetlenie", "lampa off"],
    "open_blinds": ["otwórz rolety", "odsłoń okna", "podnieś żaluzje"],
    "close_blinds": ["zamknij rolety", "zasłoń okna", "opuść żaluzje"],
    "open_locks": ["otwórz drzwi", "odblokuj zamek", "wpuść mnie", "otwórz dom"],
    "close_locks": ["zamknij drzwi", "zablokuj zamek", "zamknij dom"],
    "set_temperature": ["ustaw temperaturę", "zmień ogrzewanie", "podgrzej dom", "zrób cieplej", "schłodź dom", "zmniejsz ogrzewanie"],
    "check_weather": ["jaka jest pogoda", "podaj pogodę", "ile jest stopni na zewnątrz", "czy jest zimno"]
}

def recognize_intent(text):
    user_doc = nlp(text)
    best_match = None
    best_score = 0.65  # Odrobinę obniżony próg ułatwi łapanie wariacji słownych

    for intent, examples in intents.items():
        for example in examples:
            example_doc = nlp(example)
            similarity = user_doc.similarity(example_doc)
            if similarity > best_score:
                best_score = similarity
                best_match = intent

    return best_match