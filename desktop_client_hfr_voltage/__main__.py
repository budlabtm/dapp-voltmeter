from PyQt6.QtWidgets import QApplication
from .controller import Controller
from .settings import Settings
import sys

Settings.init()

app = QApplication([])
controller = Controller()

app.aboutToQuit.connect(controller.terminate)
sys.exit(app.exec())
