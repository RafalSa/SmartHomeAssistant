# SmartHomeAssistant 🏠✨

**SmartHomeAssistant** is an advanced, multithreaded desktop application designed to control and automate smart home ecosystems. Moving beyond simple scripts, this project showcases enterprise-level Python architecture, featuring a hardware-accelerated GUI, non-blocking voice control via a dedicated background worker, Natural Language Processing (NLP), and dynamic API integrations.

---

## 🚀 Key Features & Engineering Highlights

- **Thread-Safe Voice Assistant:** Utilizes `SpeechRecognition` and `pyttsx3` running on a dedicated daemon thread (`QThread`) with an event-driven Queue system. This ensures 0% UI freezing and features a professional **30-second conversational follow-up mode**.
- **NLP Intent Recognition:** Replaces rigid string-matching with `spaCy` NLP models to intelligently parse and understand natural language commands.
- **Hardware-Accelerated UI (PyQt6):** A modern, dark-mode dashboard featuring procedural 60-FPS Pseudo-3D animations (Additive blending fire particles, dynamic 3D door geometry, and easing curves).
- **Auto-Discovery Configuration:** Implements Configuration Management patterns. The system automatically detects its physical location via IP (`ipinfo.io`), creates an editable `home_config.json`, and fetches precise weather metrics from `Open-Meteo`.
- **Persistent State Management:** All devices (Lighting, Blinds, Locks, Heating) maintain their state in a local JSON database, ensuring consistency across application restarts.

---

## 🛠 Technology Stack

- **Core:** Python 3.10+
- **GUI & Rendering:** PyQt6 (`QPainter`, `QTimer`, `Signals & Slots`)
- **Voice & NLP:** `SpeechRecognition`, `pyttsx3`, `spaCy` (`pl_core_news_md`)
- **Networking:** `requests`, REST APIs
- **Patterns Used:** Observer (Signals), Thread Worker (Producer-Consumer), Configuration Management, Singleton-like state handling.

---

## 📂 Project Structure

```text
SmartHomeAssistant/
│
├── gui_app.py               # Main PyQt6 Application and Event Loop
├── voice_utils.py           # Thread-safe TTS/STT Queue Engine
├── intent_recognizer.py     # NLP logic and intent mapping
├── logger_setup.py          # Professional logging configuration
├── requirements.txt         # Project dependencies
├── device_states.json       # Auto-generated persistent state storage
├── home_config.json         # Auto-generated location configuration
│
└── modules/                 # Pluggable device components
    ├── base_device.py       # Base class handling JSON state reads/writes
    ├── lighting.py          # Lighting control
    ├── blinds.py            # Blinds/shutters control
    ├── locks.py             # Electric locks security module
    ├── heating.py           # Thermostat and thermodynamics
    └── weather.py           # Geolocation and Open-Meteo API integration

## 👥 Authors

- **Rafał Sak** – Project creator, Python developer, UI design, database architecture  
  GitHub: [RafalSa](https://github.com/RafalSa)  

---

## 📜 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this software for personal and commercial purposes, provided that the original author is credited.
