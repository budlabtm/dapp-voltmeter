from PyQt6.QtWidgets import QApplication
from controller import Controller
from view import MainWindow
from settings import Settings
import sys

Settings.init()

app = QApplication([])
controller = Controller()
view = MainWindow()

app.aboutToQuit.connect(controller.terminate)

view.add_stream_widget(controller.create_widget('C0', view))
view.add_stream_widget(controller.create_widget('C1', view))
view.show()

sys.exit(app.exec())
