import sys
import threading
import time
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QDialog, QSlider, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPointF
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QRadialGradient, QPolygonF, QPainterPath

import intent_recognizer
import voice_utils
from logger_setup import get_logger

from modules import lighting
from modules import blinds
from modules import locks
from modules import heating
from modules import weather

logger = get_logger("PyQt_MultiWindow_Final")


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

            # FAZA 1: Czekamy na "Witam dom"
            self.status_signal.emit("🟢 Czuwanie (Powiedz 'Witam dom')", "#00ffcc")
            wake_word = voice_utils.listen_for_input()

            if not self.is_running: break
            if not wake_word: continue

            if "witam dom" in wake_word:
                self.log_to_terminal("Wybudzono asystenta. Start sesji 30s.")
                voice_utils.say("Słucham?")

                # Zapisujemy start sesji
                session_start_time = time.time()
                session_timeout = 30  # Twoje 30 sekund

                # FAZA 2: Sesja aktywna (Pętla follow-up)
                while self.is_running:
                    # Obliczamy ile czasu zostało do końca sesji
                    time_left = int(session_timeout - (time.time() - session_start_time))

                    if time_left <= 0:
                        self.log_to_terminal("Sesja zakończona (timeout).")
                        voice_utils.say("Przechodzę w tryb czuwania.")
                        break  # Wychodzimy z sesji do Fazy 1

                    self.status_signal.emit(f"🔴 Słucham... (sesja: {time_left}s)", "#ff4d4d")

                    # Nasłuchujemy komendy
                    command = voice_utils.listen_for_input()

                    if command:
                        # Jeśli użytkownik coś powiedział, resetujemy czas sesji!
                        session_start_time = time.time()
                        self.log_to_terminal(f"Komenda: {command}")

                        if command in ["koniec", "stop", "wyłącz się"]:
                            voice_utils.say("Zamykam system.")
                            self.is_running = False
                            QApplication.quit()
                            return

                        elif command in ["idź spać", "uśpij", "dobranoc", "dziękuję"]:
                            voice_utils.say("Dobranoc.")
                            break  # Ręczne wyjście z sesji

                        intent = intent_recognizer.recognize_intent(command)
                        if intent:
                            self.execute_device_logic(intent)
                        else:
                            voice_utils.say("Nie zrozumiałam, słucham dalej.")
                    else:
                        # Jeśli była cisza, pętla leci dalej i sprawdza time_left
                        continue

    def log_to_terminal(self, message):
        """Pomocnicza funkcja do logowania w konsoli IDE"""
        logger.info(f"VOICE_CORE: {message}")

    def execute_device_logic(self, intent):
        # ... (tutaj zostawiasz swoją dotychczasową logikę if/elif dla urządzeń) ...
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
            weather.get_current_weather()

# ==========================================
# 2. SILNIKI RENDERUJĄCE (WIDOKI)
# ==========================================
class BaseAnimatedWindow(QDialog):
    def __init__(self, title, size=(350, 450), parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(*size)
        self.setStyleSheet("background-color: #121214; color: white;")
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
        super().__init__("Oświetlenie 3D", parent=parent)
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
        # Akcja bezpośrednia (Kolejka TTS w tle to obsłuży bez zacinki)
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
        self.current_angle += (self.target_angle - self.current_angle) * 0.15

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
        self.target_angle = 0.0 if is_locked else 0.8

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


class HeatWindow(BaseAnimatedWindow):
    def __init__(self, parent=None):
        super().__init__("Ogrzewanie 3D", parent=parent)

        self.temp_display = QLabel()
        self.temp_display.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.temp_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(15, 30)
        self.slider.valueChanged.connect(self.update_temp)
        self.slider.sliderReleased.connect(self.set_temp)

        self.layout.addWidget(self.temp_display)
        self.layout.addWidget(self.slider)

        self.canvas.paintEvent = self.render_scene
        self.refresh_ui()

    def render_scene(self, event):
        self.time_step += 0.12
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.canvas.width(), self.canvas.height()
        cx, cy = w / 2, h - 20

        temp = self.slider.value()
        r = min(255, int(50 + (temp - 15) * 13))
        b = max(0, int(255 - (temp - 15) * 17))
        self.temp_display.setStyleSheet(f"color: rgb({r}, 50, {b});")

        base_h = (temp - 10) * 8
        base_w = 40 + (temp - 15) * 1.5

        colors = [
            QColor(r, 50, b, 200),
            QColor(255, 120, 0, 220),
            QColor(255, 255, 100, 250)
        ]

        painter.setPen(Qt.PenStyle.NoPen)
        for i, color in enumerate(colors):
            scale = 1.0 - (i * 0.3)
            path = QPainterPath()
            start_x = cx - base_w * scale
            path.moveTo(start_x, cy)

            cp1x = cx - base_w * scale * 0.5
            cp1y = cy - base_h * scale * 0.4 + math.sin(self.time_step + i) * 15
            cp2x = cx + math.sin(self.time_step * 1.5 + i) * 20
            cp2y = cy - base_h * scale * 0.8
            endx = cx + math.sin(self.time_step * 2.5 + i) * 10
            endy = cy - base_h * scale
            path.cubicTo(cp1x, cp1y, cp2x, cp2y, endx, endy)

            cp3x = cx - math.sin(self.time_step * 1.5 + i) * 20
            cp3y = cy - base_h * scale * 0.8
            cp4x = cx + base_w * scale * 0.5
            cp4y = cy - base_h * scale * 0.4 + math.cos(self.time_step + i) * 15
            end2x = cx + base_w * scale
            end2y = cy
            path.cubicTo(cp3x, cp3y, cp4x, cp4y, end2x, end2y)
            path.lineTo(start_x, cy)

            painter.setBrush(QBrush(color))
            painter.drawPath(path)

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
        voice_utils.say(f"Piec ustawiony na {val} stopni.")


class BlindsWindow(BaseAnimatedWindow):
    def __init__(self, parent=None):
        super().__init__("Rolety 3D", parent=parent)

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
        self.current_drop += (self.target_drop - self.current_drop) * 0.1

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


# ==========================================
# 3. KONSOLA STEROWANIA (LAUNCHER)
# ==========================================
class MainLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartHome OS")
        self.setFixedSize(450, 550)
        self.setStyleSheet("background-color: #000000; color: white;")

        self.windows = {}
        self.setup_ui()

        self.worker = VoiceWorker()
        self.worker.status_signal.connect(self.update_status)
        self.worker.ui_update_signal.connect(self.refresh_window)  # NOWOŚĆ: Synchronizacja!
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
        self.mic_btn.setStyleSheet("background-color: #333; color: white; border-radius: 8px;")
        self.mic_btn.clicked.connect(self.toggle_mic)
        layout.addWidget(self.mic_btn)

        self.status_label = QLabel("Gotowość")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #888; margin-bottom: 15px;")
        layout.addWidget(self.status_label)

        grid = QGridLayout()
        grid.setSpacing(15)

        self.add_grid_button(grid, 0, 0, "💡 Oświetlenie", lambda: self.open_window("light", LightWindow))
        self.add_grid_button(grid, 0, 1, "🔥 Ogrzewanie", lambda: self.open_window("heat", HeatWindow))
        self.add_grid_button(grid, 1, 0, "🪟 Rolety", lambda: self.open_window("blinds", BlindsWindow))
        self.add_grid_button(grid, 1, 1, "🚪 Zamki", lambda: self.open_window("locks", LocksWindow))

        layout.addLayout(grid)

    def add_grid_button(self, grid, row, col, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(70)
        btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn.setStyleSheet("""
            QPushButton { background-color: #1e1e22; border-radius: 12px; }
            QPushButton:hover { background-color: #2c2c34; }
        """)
        btn.clicked.connect(callback)
        grid.addWidget(btn, row, col)

    def toggle_mic(self):
        self.worker.mic_enabled = not self.worker.mic_enabled
        if self.worker.mic_enabled:
            self.mic_btn.setText("MIKROFON: NASŁUCHUJE")
            self.mic_btn.setStyleSheet("background-color: #27ae60; color: white; border-radius: 8px;")
        else:
            self.mic_btn.setText("MIKROFON: WYŁĄCZONY")
            self.mic_btn.setStyleSheet("background-color: #333; color: white; border-radius: 8px;")

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
        """Odbiera sygnał od wątku głosowego i każe okienku pobrać nowy stan"""
        if win_id in self.windows and self.windows[win_id].isVisible():
            self.windows[win_id].refresh_ui()

    def closeEvent(self, event):
        self.worker.is_running = False
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainLauncher()
    window.show()
    sys.exit(app.exec())