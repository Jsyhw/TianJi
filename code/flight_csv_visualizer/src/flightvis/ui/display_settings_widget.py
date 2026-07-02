from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QWidget,
)

from flightvis.constants import LINE_STYLES


class DisplaySettingsWidget(QWidget):
    def __init__(self, display, title_getter, title_setter, parent=None):
        super().__init__(parent)
        self.display = display
        self.title_getter = title_getter
        self.title_setter = title_setter

        self.title = QLineEdit(title_getter())
        self.x_label = QLineEdit(display.x_label)
        self.y_label = QLineEdit(display.y_label)
        self.grid = QCheckBox()
        self.grid.setChecked(display.show_grid)
        self.legend = QCheckBox()
        self.legend.setChecked(display.show_local_legend)
        self.line_width = QDoubleSpinBox()
        self.line_width.setRange(0.1, 10.0)
        self.line_width.setSingleStep(0.1)
        self.line_width.setValue(display.line_width)
        self.line_style = QComboBox()
        self.line_style.addItems(LINE_STYLES)
        self.line_style.setCurrentText(display.line_style)

        self.x_min = QDoubleSpinBox()
        self.x_max = QDoubleSpinBox()
        self.y_min = QDoubleSpinBox()
        self.y_max = QDoubleSpinBox()
        for spin in [self.x_min, self.x_max, self.y_min, self.y_max]:
            spin.setRange(-1e12, 1e12)
            spin.setDecimals(6)
        self.use_x_range = QCheckBox("手动")
        self.use_y_range = QCheckBox("手动")
        if display.x_range:
            self.use_x_range.setChecked(True)
            self.x_min.setValue(display.x_range[0])
            self.x_max.setValue(display.x_range[1])
        if display.y_range:
            self.use_y_range.setChecked(True)
            self.y_min.setValue(display.y_range[0])
            self.y_max.setValue(display.y_range[1])

        layout = QFormLayout(self)
        layout.addRow("标题", self.title)
        layout.addRow("X轴标签", self.x_label)
        layout.addRow("Y轴标签", self.y_label)
        layout.addRow("显示网格", self.grid)
        layout.addRow("局部图例", self.legend)
        layout.addRow("线宽", self.line_width)
        layout.addRow("线型", self.line_style)
        layout.addRow("X轴范围", self._range_row(self.use_x_range, self.x_min, self.x_max))
        layout.addRow("Y轴范围", self._range_row(self.use_y_range, self.y_min, self.y_max))

    def _range_row(self, use_check, min_spin, max_spin):
        box = QGroupBox()
        layout = QHBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(use_check)
        layout.addWidget(min_spin)
        layout.addWidget(max_spin)
        return box

    def apply(self) -> None:
        self.title_setter(self.title.text().strip() or "未命名图窗")
        self.display.x_label = self.x_label.text().strip() or "time"
        self.display.y_label = self.y_label.text().strip() or "value"
        self.display.show_grid = self.grid.isChecked()
        self.display.show_local_legend = self.legend.isChecked()
        self.display.line_width = float(self.line_width.value())
        self.display.line_style = self.line_style.currentText()
        self.display.x_range = (self.x_min.value(), self.x_max.value()) if self.use_x_range.isChecked() else None
        self.display.y_range = (self.y_min.value(), self.y_max.value()) if self.use_y_range.isChecked() else None
