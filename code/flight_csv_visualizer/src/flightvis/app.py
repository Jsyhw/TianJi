import sys

from PySide6.QtWidgets import QApplication

from flightvis.plotting.style import configure_matplotlib_fonts
from flightvis.ui.main_window import MainWindow


def main() -> int:
    configure_matplotlib_fonts()
    app = QApplication(sys.argv)
    app.setApplicationName("FlightCSVVisualizer")
    window = MainWindow()
    window.resize(1500, 900)
    window.show()
    return app.exec()
