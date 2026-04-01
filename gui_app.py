import sys
import threading
import time
import math
import random
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QDialog, QSlider, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPointF
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QRadialGradient, QPolygonF, QPainterPath, QLinearGradient

import intent_recognizer
import voice_utils
from logger_setup import get_logger

from modules import lighting
from modules import blinds
from modules import locks
from modules import heating
from modules import weather

logger = get_logger("PyQt_Enterprise_Edition")


# ==========================================
# 1. ZARZĄDCA LOGIKI (VOICE WORKER)
# ==========================================
class VoiceWorker(QThread):
    status_signal = pyqtSignal(str, str)
    ui_update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.mic_enabled = False

    def run(self):
        time.sleep(0.5)
        while self.is_running:
            if not self.mic_enabled:
                self.status_signal.emit("Zasilanie mikrofonu: ODCIĘTE", "#555555")
                time.sleep(0.5)
                continue

            self.status_signal.emit("🟢 Czuwanie (Powiedz 'Witam dom')", "#00ffcc")
            wake_word = voice_utils.listen_for_input()

            if not self.is_running: break
            if not wake_word: continue

            if "witam dom" in wake_word:
                logger.info("VOICE_CORE: Wybudzono asystenta. Start sesji 30s.")
                voice_utils.say("Słucham?")

                session_start_time = time.time()
                session_timeout = 30

                while self.is_running:
                    time_left = int(session_timeout - (time.time() - session_start_time))

                    if time_left <= 0:
                        logger.info("VOICE_CORE: Sesja zakończona (timeout).")
                        voice_utils.say("Przechodzę w tryb czuwania.")
                        break

                    self.status_signal.emit(f"🔴 Słucham... (sesja: {time_left}s)", "#ff4d4d")

                    command = voice_utils.listen_for_input()

                    if command:
                        session_start_time = time.time()
                        logger.info(f"VOICE_CORE: Komenda: {command}")

                        if command in ["koniec", "stop", "wyłącz się"]:
                            voice_utils.say("Zamykam system.")
                            self.is_running = False
                            QApplication.quit()
                            return

                        elif command in ["idź spać", "uśpij", "dobranoc", "dziękuję"]:
                            voice_utils.say("Dobranoc.")
                            break

                        intent = intent_recognizer.recognize_intent(command)
                        if intent:
                            self.execute_device_logic(intent)
                        else:
                            voice_utils.say("Nie zrozumiałam, słucham dalej.")
                    else:
                        continue

    def execute_device_logic(self, intent):
        if intent == "turn_on_lights":
            lighting.living_room_light.turn_on()
            self.ui_update_signal.emit("light")
        elif intent == "turn_off_lights":
            lighting.living_room_light.turn_off()
            self.ui_update_signal.emit("light")
        elif intent == "open_blinds":
            blinds.main_blinds.open()
            self.ui_update_signal.emit("blinds")
        elif intent == "close_blinds":
            blinds.main_blinds.close()
            self.ui_update_signal.emit("blinds")
        elif intent == "open_locks":
            locks.front_door.open()
            self.ui_update_signal.emit("locks")
        elif intent == "close_locks":
            locks.front_door.close()
            self.ui_update_signal.emit("locks")
        elif intent == "set_temperature":
            heating.home_heater.set_temperature()
            self.ui_update_signal.emit("heat")
        elif intent == "check_weather":
            # Zamiast tylko mówić o otwieraniu stacji, uruchamiamy w tle właściwy moduł pogody.
            # Plik weather.py połączy się z API i samodzielnie wywoła funkcję say() z temperaturą.
            import threading
            threading.Thread(target=weather.get_current_weather, daemon=True).start()
            # Jednocześnie odświeżamy okienko pogodowe (jeśli jest akurat otwarte na ekranie)
            self.ui_update_signal.emit("weather")


# ==========================================
# 2. SILNIKI RENDERUJĄCE (WIDOKI 60FPS)
# ==========================================
class BaseAnimatedWindow(QDialog):
    def __init__(self, title, size=(350, 450), parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(*size)
        self.setStyleSheet("background-color: #0A0A0C; color: white;")
        self.layout = QVBoxLayout(self)

        self.canvas = QWidget()
        self.canvas.setMinimumHeight(250)
        self.layout.addWidget(self.canvas)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.canvas.update)
        self.anim_timer.start(16)
        self.time_step = 0.0


class LightWindow(BaseAnimatedWindow):
    def __init__(self, parent=None):
        super().__init__("Oświetlenie", parent=parent)
        self.btn = QPushButton()
        self.btn.setFixedHeight(50)
        self.btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn.clicked.connect(self.toggle)
        self.layout.addWidget(self.btn)
        self.canvas.paintEvent = self.render_scene
        self.refresh_ui()

    def render_scene(self, event):
        self.time_step += 0.05
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.canvas.width(), self.canvas.height()
        cx, cy = w / 2, h / 2
        is_on = lighting.living_room_light.state.get('is_on', False)

        if is_on:
            pulse = math.sin(self.time_step) * 5
            grad = QRadialGradient(cx, cy, 120 + pulse)
            grad.setColorAt(0, QColor(255, 255, 150, 150))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 120 + pulse, 120 + pulse)

            painter.setBrush(QBrush(QColor(255, 255, 220)))
            painter.setPen(QPen(QColor(255, 255, 100), 2))
        else:
            painter.setBrush(QBrush(QColor(30, 30, 30)))
            painter.setPen(QPen(QColor(80, 80, 80), 2))

        painter.drawEllipse(QPointF(cx, cy), 40, 40)
        painter.setBrush(QBrush(QColor(80, 80, 80)))
        painter.drawRect(int(cx - 15), int(cy + 40), 30, 20)

    def refresh_ui(self):
        if lighting.living_room_light.state.get('is_on', False):
            self.btn.setText("ZGAŚ ŚWIATŁO")
            self.btn.setStyleSheet("background-color: #f1c40f; color: black; border-radius: 8px;")
        else:
            self.btn.setText("ZAPAL ŚWIATŁO")
            self.btn.setStyleSheet("background-color: #333; color: white; border-radius: 8px;")

    def toggle(self):
        if lighting.living_room_light.state.get('is_on', False):
            lighting.living_room_light.turn_off()
        else:
            lighting.living_room_light.turn_on()
        self.refresh_ui()


class LocksWindow(BaseAnimatedWindow):
    def __init__(self, parent=None):
        super().__init__("Zamek 3D", parent=parent)
        self.btn = QPushButton()
        self.btn.setFixedHeight(50)
        self.btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn.clicked.connect(self.toggle)
        self.layout.addWidget(self.btn)

        self.current_angle = 0.0
        self.target_angle = 0.0
        self.canvas.paintEvent = self.render_scene
        self.refresh_ui()

    def render_scene(self, event):
        # Nieliniowa interpolacja (Ease-Out) - drzwi miękko hamują na końcu
        self.current_angle += (self.target_angle - self.current_angle) * 0.12

        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.canvas.width(), self.canvas.height()
        door_w, door_h = 120, 200
        x0, y0 = w / 2 - door_w / 2, h / 2 - door_h / 2

        painter.setPen(QPen(QColor(50, 50, 50), 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(int(x0), int(y0), door_w, door_h)

        proj_w = door_w * math.cos(self.current_angle * (math.pi / 2))
        y_offset = 20 * math.sin(self.current_angle * (math.pi / 2))

        poly = QPolygonF([
            QPointF(x0, y0),
            QPointF(x0 + proj_w, y0 + y_offset),
            QPointF(x0 + proj_w, y0 + door_h - y_offset),
            QPointF(x0, y0 + door_h)
        ])

        painter.setBrush(QBrush(QColor(139, 69, 19)))
        painter.setPen(QPen(QColor(92, 46, 12), 2))
        painter.drawPolygon(poly)

        handle_x = x0 + proj_w * 0.8
        handle_y = y0 + door_h / 2
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawEllipse(QPointF(handle_x, handle_y), 5, 10)

    def refresh_ui(self):
        is_locked = locks.front_door.state.get('is_locked', True)
        self.target_angle = 0.0 if is_locked else 0.85
        if is_locked:
            self.btn.setText("ODBLOKUJ DRZWI")
            self.btn.setStyleSheet("background-color: #c0392b; color: white; border-radius: 8px;")
        else:
            self.btn.setText("ZABLOKUJ DRZWI")
            self.btn.setStyleSheet("background-color: #27ae60; color: white; border-radius: 8px;")

    def toggle(self):
        if locks.front_door.state.get('is_locked', True):
            locks.front_door.open()
        else:
            locks.front_door.close()
        self.refresh_ui()


class BlindsWindow(BaseAnimatedWindow):
    def __init__(self, parent=None):
        super().__init__("Rolety", parent=parent)
        btn_layout = QVBoxLayout()
        btn_up = QPushButton("⬆ OTWÓRZ")
        btn_down = QPushButton("⬇ ZAMKNIJ")
        for btn in [btn_up, btn_down]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("background-color: #2980b9; color: white; border-radius: 8px;")
            btn_layout.addWidget(btn)

        btn_up.clicked.connect(lambda: self.toggle(True))
        btn_down.clicked.connect(lambda: self.toggle(False))
        self.layout.addLayout(btn_layout)

        self.current_drop = 0.0
        self.target_drop = 0.0
        self.canvas.paintEvent = self.render_scene
        self.refresh_ui()

    def render_scene(self, event):
        self.current_drop += (self.target_drop - self.current_drop) * 0.08

        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.canvas.width(), self.canvas.height()

        painter.setBrush(QBrush(QColor(135, 206, 235)))
        painter.drawRect(20, 20, w - 40, h - 40)
        painter.setBrush(QBrush(QColor(255, 255, 100)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(w / 2, h / 3), 30, 30)

        clip_h = int((h - 40) * self.current_drop)
        painter.setClipRect(20, 20, w - 40, clip_h)

        num_slats = 15
        slat_h = (h - 40) / num_slats
        painter.setPen(QPen(QColor(30, 30, 30), 1))
        for i in range(num_slats):
            y_pos = 20 + i * slat_h
            painter.setBrush(QBrush(QColor(80, 80, 80)))
            painter.drawRect(20, int(y_pos), w - 40, int(slat_h / 2))
            painter.setBrush(QBrush(QColor(50, 50, 50)))
            painter.drawRect(20, int(y_pos + slat_h / 2), w - 40, int(slat_h / 2))

    def refresh_ui(self):
        is_open = blinds.main_blinds.state.get('is_open', False)
        self.target_drop = 0.0 if is_open else 1.0

    def toggle(self, is_open):
        if is_open:
            blinds.main_blinds.open()
        else:
            blinds.main_blinds.close()
        self.refresh_ui()


# --- 3. FOTOREALISTYCZNY OGIEŃ (ADDITIVE BLENDING) ---
class HeatWindow(BaseAnimatedWindow):
    def __init__(self, parent=None):
        super().__init__("Termodynamika PRO", parent=parent)
        self.temp_display = QLabel()
        self.temp_display.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.temp_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(15, 30)
        self.slider.valueChanged.connect(self.update_temp)
        self.slider.sliderReleased.connect(self.set_temp)

        self.layout.addWidget(self.temp_display)
        self.layout.addWidget(self.slider)

        # System cząsteczek ognia
        self.particles = []
        for _ in range(40):
            self.particles.append(self.spawn_particle())

        self.canvas.paintEvent = self.render_scene
        self.refresh_ui()

    def spawn_particle(self):
        """Generuje pojedynczy język ognia lub iskrę"""
        return {
            'x_offset': random.uniform(-40, 40),
            'y_offset': random.uniform(0, 30),
            'life': random.uniform(0.0, 1.0),
            'speed': random.uniform(0.02, 0.05),
            'scale': random.uniform(0.5, 1.5),
            'phase': random.uniform(0, math.pi * 2)
        }

    def render_scene(self, event):
        self.time_step += 0.1
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # MAGICZNY TRYB: Mieszanie Addytywne - nakładające się kolory stają się białe (jak prawdziwy ogień!)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)

        w, h = self.canvas.width(), self.canvas.height()
        cx, cy = w / 2, h - 30

        temp = self.slider.value()
        intensity = (temp - 15) / 15.0  # 0.0 - 1.0

        # Kolor tekstu
        r_text = min(255, int(150 + intensity * 105))
        self.temp_display.setStyleSheet(f"color: rgb({r_text}, 80, 20);")

        # Baza - żarzące się węgle
        painter.setPen(Qt.PenStyle.NoPen)
        base_color = QColor(200, 30, 0, int(100 + intensity * 100))
        painter.setBrush(QBrush(base_color))
        painter.drawEllipse(QPointF(cx, cy), 50 + intensity * 20, 15)

        # Rysowanie dynamicznego systemu cząsteczek
        for p in self.particles:
            p['life'] += p['speed']
            if p['life'] >= 1.0:
                p.update(self.spawn_particle())  # Odradzanie u dołu
                p['life'] = 0.0

            # Matematyka ruchu pojedynczego płomienia
            life_inv = 1.0 - p['life']
            current_x = cx + p['x_offset'] * life_inv + math.sin(self.time_step + p['phase']) * 15 * life_inv
            current_y = cy + p['y_offset'] - (p['life'] * (100 + intensity * 150))

            # Płomień kurczy się ku górze i zanika
            size = 25 * p['scale'] * life_inv * (0.5 + intensity * 0.5)
            opacity = int(255 * math.sin(p['life'] * math.pi))  # Wygaszanie

            # Wewnętrzny gradient cząsteczki
            grad = QRadialGradient(current_x, current_y, size)
            grad.setColorAt(0, QColor(255, 50 + int(p['life'] * 150), 0, opacity))  # Czerwony w pomarańcz
            grad.setColorAt(1, QColor(0, 0, 0, 0))

            painter.setBrush(QBrush(grad))
            painter.drawEllipse(QPointF(current_x, current_y), size, size * 1.5)

    def refresh_ui(self):
        temp = heating.home_heater.state.get('temperature', 21)
        self.slider.setValue(temp)
        self.update_temp(temp)

    def update_temp(self, val):
        self.temp_display.setText(f"{val}°C")

    def set_temp(self):
        val = self.slider.value()
        heating.home_heater.state['temperature'] = val
        heating.home_heater.save_state()
        threading.Thread(target=voice_utils.say, args=(f"Piec. {val} stopni.",), daemon=True).start()


# --- 4. PROCEDURALNE OKNO POGODOWE (CHORZÓW API) ---
class WeatherWorker(QThread):
    data_signal = pyqtSignal(float, int)  # temp, wmo_code

    def run(self):
        try:
            # Dynamiczne pobieranie danych pogodowych dla Chorzowa (WSB Merito)
            url = "https://api.open-meteo.com/v1/forecast?latitude=50.30&longitude=18.95&current_weather=true"
            response = requests.get(url, timeout=5).json()
            temp = response['current_weather']['temperature']
            code = response['current_weather']['weathercode']
            self.data_signal.emit(temp, code)
        except Exception as e:
            logger.error(f"Weather API Error: {e}")


class WeatherWindow(BaseAnimatedWindow):
    def __init__(self, parent=None):
        super().__init__("Stacja Meteo", size=(350, 400), parent=parent)
        self.info_label = QLabel("Łączenie z satelitą...")
        self.info_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.temp = 0.0
        self.weather_code = 0  # 0=Sun, 51=Rain, 71=Snow
        self.particles = [{'x': random.uniform(0, 350), 'y': random.uniform(0, 250), 'speed': random.uniform(5, 15)} for
                          _ in range(50)]

        self.canvas.paintEvent = self.render_scene
        self.fetch_weather()

    def fetch_weather(self):
        self.worker = WeatherWorker()
        self.worker.data_signal.connect(self.update_data)
        self.worker.start()

    def update_data(self, temp, code):
        self.temp = temp
        self.weather_code = code
        desc = "Bezchmurnie" if code == 0 else "Pochmurno/Deszcz" if code > 50 else "Pochmurno"
        self.info_label.setText(f"Chorzów: {self.temp}°C\n{desc}")

    def render_scene(self, event):
        self.time_step += 0.05
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.canvas.width(), self.canvas.height()

        # Tło nieba
        sky_color = QColor(135, 206, 235) if self.weather_code < 50 else QColor(70, 80, 90)
        painter.setBrush(QBrush(sky_color))
        painter.drawRect(0, 0, w, h)

        # Proceduralna Generacja Zjawisk
        if self.weather_code == 0 or self.weather_code in [1, 2]:
            # Słońce
            cx, cy = w / 2, h / 2
            painter.setPen(Qt.PenStyle.NoPen)
            # Promienie słoneczne z efektem pulsacji
            pulse = math.sin(self.time_step * 2) * 5
            painter.setBrush(QBrush(QColor(255, 255, 100, 150)))
            painter.drawEllipse(QPointF(cx, cy), 60 + pulse, 60 + pulse)
            painter.setBrush(QBrush(QColor(255, 220, 50)))
            painter.drawEllipse(QPointF(cx, cy), 45, 45)

        if self.weather_code >= 50:
            # Deszcz lub Śnieg
            painter.setPen(QPen(QColor(200, 200, 255, 180), 2))
            for p in self.particles:
                p['y'] += p['speed']
                if p['y'] > h:
                    p['y'] = -10
                    p['x'] = random.uniform(0, w)

                # Zależnie czy pada deszcz czy śnieg (kody WMO)
                if self.weather_code >= 71 and self.weather_code <= 86:
                    # Śnieg (dryfujący)
                    p['x'] += math.sin(self.time_step + p['y'] / 50.0) * 1.5
                    painter.setBrush(QBrush(QColor(255, 255, 255)))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(QPointF(p['x'], p['y']), 3, 3)
                else:
                    # Deszcz
                    painter.drawLine(int(p['x']), int(p['y']), int(p['x'] - 2), int(p['y'] + 10))


# ==========================================
# 4. KONSOLA STEROWANIA (LAUNCHER)
# ==========================================
class MainLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartHome OS Pro")
        self.setFixedSize(450, 600)
        self.setStyleSheet("background-color: #050505; color: white;")

        self.windows = {}
        self.setup_ui()

        self.worker = VoiceWorker()
        self.worker.status_signal.connect(self.update_status)
        self.worker.ui_update_signal.connect(self.refresh_window)
        self.worker.start()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("SmartHome OS")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.mic_btn = QPushButton("MIKROFON: WYŁĄCZONY")
        self.mic_btn.setFixedHeight(40)
        self.mic_btn.setStyleSheet("background-color: #222; color: white; border-radius: 8px;")
        self.mic_btn.clicked.connect(self.toggle_mic)
        layout.addWidget(self.mic_btn)

        self.status_label = QLabel("Gotowość systemu")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(self.status_label)

        grid = QGridLayout()
        grid.setSpacing(15)

        self.add_grid_button(grid, 0, 0, "💡 Oświetlenie", lambda: self.open_window("light", LightWindow))
        self.add_grid_button(grid, 0, 1, "🔥 Ogrzewanie", lambda: self.open_window("heat", HeatWindow))
        self.add_grid_button(grid, 1, 0, "🪟 Rolety", lambda: self.open_window("blinds", BlindsWindow))
        self.add_grid_button(grid, 1, 1, "🚪 Zamki", lambda: self.open_window("locks", LocksWindow))

        # Nowy dedykowany przycisk dla Pogody
        weather_btn = QPushButton("🌤 Stacja Pogodowa")
        weather_btn.setFixedHeight(50)
        weather_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        weather_btn.setStyleSheet("background-color: #0f3460; border-radius: 12px;")
        weather_btn.clicked.connect(lambda: self.open_window("weather", WeatherWindow))

        layout.addLayout(grid)
        layout.addWidget(weather_btn)

    def add_grid_button(self, grid, row, col, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(70)
        btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn.setStyleSheet(
            "QPushButton { background-color: #1a1a1e; border-radius: 12px; } QPushButton:hover { background-color: #2c2c34; }")
        btn.clicked.connect(callback)
        grid.addWidget(btn, row, col)

    def toggle_mic(self):
        self.worker.mic_enabled = not self.worker.mic_enabled
        if self.worker.mic_enabled:
            self.mic_btn.setText("MIKROFON: AKTYWNY")
            self.mic_btn.setStyleSheet("background-color: #e84118; color: white; border-radius: 8px;")
        else:
            self.mic_btn.setText("MIKROFON: WYŁĄCZONY")
            self.mic_btn.setStyleSheet("background-color: #222; color: white; border-radius: 8px;")

    def update_status(self, text, color="#aaaaaa"):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; margin-bottom: 15px;")

    def open_window(self, win_id, window_class):
        if win_id not in self.windows or not self.windows[win_id].isVisible():
            self.windows[win_id] = window_class(self)
            self.windows[win_id].show()
        else:
            self.windows[win_id].activateWindow()

    def refresh_window(self, win_id):
        if win_id in self.windows and self.windows[win_id].isVisible():
            if win_id == "weather":
                self.windows[win_id].fetch_weather()  # Odśwież dane z API
            else:
                self.windows[win_id].refresh_ui()

    def closeEvent(self, event):
        self.worker.is_running = False
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainLauncher()
    window.show()
    sys.exit(app.exec())