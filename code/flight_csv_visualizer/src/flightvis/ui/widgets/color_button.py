from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton


class ColorButton(QPushButton):
    color_changed = Signal(str)

    def __init__(self, color: str = "#1f77b4", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(28, 22)
        self.clicked.connect(self.choose_color)
        self.set_color(color)

    @property
    def color(self) -> str:
        return self._color

    def set_color(self, color: str) -> None:
        self._color = color
        self.setStyleSheet(f"background-color: {color}; border: 1px solid #777;")

    def choose_color(self) -> None:
        selected = QColorDialog.getColor(QColor(self._color), self, "选择颜色")
        if not selected.isValid():
            return
        color = selected.name()
        self.set_color(color)
        self.color_changed.emit(color)
