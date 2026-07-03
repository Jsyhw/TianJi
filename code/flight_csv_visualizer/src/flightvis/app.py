import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from flightvis.constants import APP_NAME
from flightvis.plotting.style import configure_matplotlib_fonts
from flightvis.resources import app_icon_path
from flightvis.ui.main_window import MainWindow


def main() -> int:
    configure_matplotlib_fonts()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon(str(app_icon_path())))
    window = MainWindow()
    window.resize(1500, 900)
    window.show()
    return app.exec()
