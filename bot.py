import sys
import time
import os
from PyQt5 import QtWidgets, QtCore
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import chess
import chess.engine
import pyautogui
import logging

logging.basicConfig(
    filename="bot_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def square_to_screen(square, x0, y0, square_width, square_height, playing_as_white=True):
    file = ord(square[0]) - ord('a')
    rank = 8 - int(square[1])

    if not playing_as_white:
        file = 7 - file
        rank = 7 - rank

    x = x0 + file * square_width + square_width / 2
    y = y0 + rank * square_height + square_height / 2
    return x, y

class BotWorker(QtCore.QThread):
    update_status = QtCore.pyqtSignal(str)
    update_move = QtCore.pyqtSignal(str)
    move_played = QtCore.pyqtSignal(str, bool)

    def __init__(self, driver, delay, play_white, auto_click, calibration_data):
        super().__init__()
        self.driver = driver
        self.delay = delay
        self.play_white = play_white
        self.auto_click = auto_click
        self.running = True
        self.engine = None
        self.calibration_data = calibration_data

    def run(self):
        self.update_status.emit("Bot actif - en attente de votre tour...")
        self.engine = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-mac")

        last_move_count = -1
        last_board_state = None

        while self.running:
            time.sleep(self.delay)

            try:
                nodes = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "wc-simple-move-list span.node-highlight-content"
                )
                san_moves = [n.text.strip() for n in nodes if n.text.strip()]
                current_move_count = len(san_moves)
            except Exception:
                continue

            if current_move_count == last_move_count:
                continue

            board = chess.Board()
            for san in san_moves:
                try:
                    board.push_san(san)
                except Exception as e:
                    logging.warning(f"Erreur en ajoutant le coup {san}: {e}")
                    continue

            is_white_turn = board.turn

            if is_white_turn != self.play_white:
                self.update_status.emit("En attente du coup adverse...")
                last_move_count = current_move_count
                last_board_state = board.copy()
                continue

            if last_board_state and board.fen() == last_board_state.fen():
                continue

            if board.is_game_over():
                self.update_status.emit("Partie terminée.")
                break

            self.update_status.emit("Calcul du meilleur coup...")

            try:
                result = self.engine.play(board, chess.engine.Limit(time=0.1))
                move = result.move
                san_move = board.san(move)

                self.update_move.emit(f"Coup conseillé : {san_move}")
                self.move_played.emit(san_move, self.play_white)
                logging.info(f"Coup proposé : {san_move} (FEN: {board.fen()})")

                if self.auto_click:
                    self.update_status.emit("Exécution du clic...")
                    self.play_move_on_screen(move.uci())
                    time.sleep(0.5)

                last_move_count = current_move_count
                last_board_state = board.copy()

            except Exception as e:
                logging.error(f"Erreur lors du calcul du coup : {e}")
                self.update_status.emit("Erreur lors du calcul du coup")

        if self.engine:
            self.engine.quit()

        self.update_status.emit("Bot arrêté.")

    def stop(self):
        self.running = False

    def play_move_on_screen(self, uci_move):
        from_square = uci_move[:2]
        to_square = uci_move[2:]

        x0, y0, square_width, square_height = self.calibration_data
        x1, y1 = square_to_screen(from_square, x0, y0, square_width, square_height, self.play_white)
        x2, y2 = square_to_screen(to_square, x0, y0, square_width, square_height, self.play_white)

        pyautogui.moveTo(x1, y1)
        pyautogui.click()
        time.sleep(0.1)
        pyautogui.moveTo(x2, y2)
        pyautogui.click()

class ChessBot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.worker = None
        self.selected_color = None
        self.calibration_data = None
        self.setup_ui()
        self.load_calibration()

    def setup_ui(self):
        self.setWindowTitle("chess.com Bot  /  v1")
        self.setMinimumSize(600, 750)

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 13px;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                margin: 4px;
            }
            QPushButton#openBrowserButton {
                background-color: #007bff;
                color: white;
            }
            QPushButton#openBrowserButton:hover {
                background-color: #3399ff;
            }
            QPushButton#calibrateButton {
                background-color: #ffc107;
                color: black;
            }
            QPushButton#startButton {
                background-color: #28a745;
                color: white;
            }
            QPushButton#startButton:disabled {
                background-color: #666666;
                color: #cccccc;
            }
            QPushButton#stopButton {
                background-color: #666666;
                color: white;
            }
            QPushButton#stopButton:enabled {
                background-color: #dc3545;
            }
            QPushButton.colorButton {
                background-color: #3c3c3c;
                color: white;
            }
            QPushButton.colorButton[selected="true"] {
                border: 2px solid #4a90e2;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                font-weight: bold;
                color: #4a90e2;
            }
            QLabel {
                padding: 4px;
            }
        """)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title_label = QtWidgets.QLabel("chess.com Bot")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4a90e2;")

        # Statut
        status_group = QtWidgets.QGroupBox("Statut")
        status_layout = QtWidgets.QVBoxLayout()
        self.status_label = QtWidgets.QLabel("En attente...")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.move_label = QtWidgets.QLabel("Coup conseillé : -")
        self.move_label.setAlignment(QtCore.Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.move_label)
        status_group.setLayout(status_layout)

        # Navigateur
        browser_group = QtWidgets.QGroupBox("Navigateur")
        browser_layout = QtWidgets.QVBoxLayout()
        self.open_browser_button = QtWidgets.QPushButton("Ouvrir Chrome")
        self.open_browser_button.setObjectName("openBrowserButton")
        self.calibrate_button = QtWidgets.QPushButton("Calibrer l'échiquier")
        self.calibrate_button.setObjectName("calibrateButton")
        self.calibrate_button.setEnabled(False)
        browser_layout.addWidget(self.open_browser_button)
        browser_layout.addWidget(self.calibrate_button)
        browser_group.setLayout(browser_layout)

        # Paramètres
        settings_group = QtWidgets.QGroupBox("Paramètres partie")
        settings_layout = QtWidgets.QVBoxLayout()
        color_label = QtWidgets.QLabel("Choisissez votre couleur :")
        color_layout = QtWidgets.QHBoxLayout()
        self.white_button = QtWidgets.QPushButton("Blanc")
        self.white_button.setCheckable(True)
        self.white_button.setProperty("selected", False)
        self.white_button.setProperty("class", "colorButton")
        self.black_button = QtWidgets.QPushButton("Noir")
        self.black_button.setCheckable(True)
        self.black_button.setProperty("selected", False)
        self.black_button.setProperty("class", "colorButton")
        color_layout.addWidget(self.white_button)
        color_layout.addWidget(self.black_button)

        options_layout = QtWidgets.QHBoxLayout()
        self.auto_click_checkbox = QtWidgets.QCheckBox("Clic automatique")
        self.auto_click_checkbox.setChecked(True)
        delay_label = QtWidgets.QLabel("Délai :")
        self.delay_input = QtWidgets.QSpinBox()
        self.delay_input.setRange(1, 10)
        self.delay_input.setValue(1)
        self.delay_input.setSuffix(" sec")
        options_layout.addWidget(self.auto_click_checkbox)
        options_layout.addStretch()
        options_layout.addWidget(delay_label)
        options_layout.addWidget(self.delay_input)

        settings_layout.addWidget(color_label)
        settings_layout.addLayout(color_layout)
        settings_layout.addLayout(options_layout)
        settings_group.setLayout(settings_layout)

        # Historique
        history_group = QtWidgets.QGroupBox("Historique des coups")
        history_layout = QtWidgets.QVBoxLayout()
        self.history_list = QtWidgets.QListWidget()
        self.history_list.setMaximumHeight(150)
        history_layout.addWidget(self.history_list)
        history_group.setLayout(history_layout)

        # Contrôles
        controls_layout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("Démarrer le Bot")
        self.start_button.setObjectName("startButton")
        self.start_button.setEnabled(False)
        self.stop_button = QtWidgets.QPushButton("Arrêter le Bot")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)

        # Ajout
        main_layout.addWidget(title_label)
        main_layout.addWidget(status_group)
        main_layout.addWidget(browser_group)
        main_layout.addWidget(settings_group)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(history_group)

        self.setLayout(main_layout)

        self.open_browser_button.clicked.connect(self.open_browser)
        self.calibrate_button.clicked.connect(self.calibrate_board)
        self.white_button.clicked.connect(lambda: self.select_color(True))
        self.black_button.clicked.connect(lambda: self.select_color(False))
        self.start_button.clicked.connect(self.start_bot)
        self.stop_button.clicked.connect(self.stop_bot)

    def calibrate_board(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Calibration")
        msg.setText("Placez la souris sur le coin supérieur gauche.\nAppuyez sur Entrée ou cliquez OK.")
        msg.exec_()
        x0, y0 = pyautogui.position()

        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Calibration")
        msg.setText("Placez la souris sur le coin inférieur droit.\nAppuyez sur Entrée ou cliquez OK.")
        msg.exec_()
        x1, y1 = pyautogui.position()

        square_width = (x1 - x0) / 8
        square_height = (y1 - y0) / 8
        self.calibration_data = (x0, y0, square_width, square_height)

        with open("calibration.txt", "w") as f:
            f.write(f"{x0},{y0},{square_width},{square_height}")

        self.status_label.setText("Calibration enregistrée.")
        if self.selected_color and self.driver:
            self.start_button.setEnabled(True)

    def load_calibration(self):
        if os.path.exists("calibration.txt"):
            try:
                with open("calibration.txt", "r") as f:
                    parts = f.read().strip().split(",")
                    if len(parts) == 4:
                        self.calibration_data = tuple(float(p) for p in parts)
                        self.status_label.setText("Calibration chargée.")
            except Exception:
                pass

    def open_browser(self):
        self.status_label.setText("Ouverture de Chrome...")
        try:
            service = Service("/usr/local/bin/chromedriver")
            options = webdriver.ChromeOptions()
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.get("https://www.chess.com/play/computer")
            self.status_label.setText("Chrome prêt.")
            self.calibrate_button.setEnabled(True)
        except Exception:
            self.status_label.setText("Erreur lors de l'ouverture de Chrome.")

    def select_color(self, is_white):
        self.selected_color = is_white
        if self.calibration_data and self.driver:
            self.start_button.setEnabled(True)

        self.white_button.setProperty("selected", is_white)
        self.black_button.setProperty("selected", not is_white)
        self.white_button.style().unpolish(self.white_button)
        self.white_button.style().polish(self.white_button)
        self.black_button.style().unpolish(self.black_button)
        self.black_button.style().polish(self.black_button)

    def start_bot(self):
        if not self.driver:
            self.status_label.setText("Veuillez ouvrir Chrome.")
            return
        if not self.calibration_data:
            self.status_label.setText("Veuillez calibrer l'échiquier.")
            return
        if self.selected_color is None:
            self.status_label.setText("Veuillez choisir une couleur.")
            return

        self.history_list.clear()

        delay = self.delay_input.value()
        auto_click = self.auto_click_checkbox.isChecked()

        self.worker = BotWorker(self.driver, delay, self.selected_color, auto_click, self.calibration_data)
        self.worker.update_status.connect(self.status_label.setText)
        self.worker.update_move.connect(self.move_label.setText)
        self.worker.move_played.connect(self.add_move_to_history)
        self.worker.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_bot(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.status_label.setText("Bot arrêté")
        self.move_label.setText("Coup conseillé : -")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def add_move_to_history(self, move, is_white):
        color = "Blanc" if is_white else "Noir"
        self.history_list.addItem(f"{color} : {move}")
        if self.history_list.count() > 10:
            self.history_list.takeItem(0)
        self.history_list.scrollToBottom()

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        if self.driver:
            self.driver.quit()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    bot = ChessBot()
    bot.show()
    sys.exit(app.exec_())
