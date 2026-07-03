from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from flightvis.ui.add_curve_widget import AddCurveWidget
from flightvis.ui.compare_mode_widget import HorizontalCompareDialog, VerticalCompareDialog
from flightvis.ui.display_settings_widget import DisplaySettingsWidget


class PlotSettingsWidget(QWidget):
    def __init__(self, plot_config, data_manager, parent=None):
        super().__init__(parent)
        self.plot_config = plot_config
        self.data_manager = data_manager
        self.display = DisplaySettingsWidget(
            plot_config.display,
            lambda: plot_config.title,
            lambda value: setattr(plot_config, "title", value),
        )
        self.mode_label = QLabel()

        mode_row = QWidget()
        mode_layout = QHBoxLayout(mode_row)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(6)
        mode_title = QLabel("绘图模式")
        horizontal = QPushButton("横向对比设置")
        vertical = QPushButton("纵向对比设置")
        manual = QPushButton("清除对比模式")
        for button in [horizontal, vertical, manual]:
            button.setFixedHeight(24)
        mode_row.setFixedHeight(30)
        mode_layout.addWidget(mode_title)
        mode_layout.addWidget(self.mode_label)
        mode_layout.addStretch(1)
        mode_layout.addWidget(horizontal)
        mode_layout.addWidget(vertical)
        mode_layout.addWidget(manual)

        layout = QVBoxLayout(self)
        layout.addWidget(mode_row)
        layout.addWidget(self.display)
        horizontal.clicked.connect(self.open_horizontal)
        vertical.clicked.connect(self.open_vertical)
        manual.clicked.connect(self.clear_compare_mode)
        self.update_mode_label()

    def update_mode_label(self) -> None:
        self.mode_label.setText(f"当前模式：{mode_label(self.plot_config.plot_mode)}")

    def open_horizontal(self) -> None:
        dialog = HorizontalCompareDialog(self.plot_config, self.data_manager, self)
        if dialog.exec():
            self.update_mode_label()

    def open_vertical(self) -> None:
        dialog = VerticalCompareDialog(self.plot_config, self.data_manager, self)
        if dialog.exec():
            self.update_mode_label()

    def clear_compare_mode(self) -> None:
        self.plot_config.plot_mode = "manual"
        self.plot_config.horizontal_compare.enabled = False
        self.plot_config.vertical_compare.enabled = False
        self.update_mode_label()

    def apply(self) -> None:
        self.display.apply()


class CustomPlotSettingsDialog(QDialog):
    def __init__(self, plot_config, data_manager, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义图窗设置")
        self.settings = PlotSettingsWidget(plot_config, data_manager)
        self.add_curve = AddCurveWidget(plot_config, data_manager, project)
        tabs = QTabWidget()
        tabs.addTab(self.settings, "绘图设置")
        tabs.addTab(self.add_curve, "添加曲线")
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(buttons)
        self.resize(680, 640)

    def accept(self) -> None:
        self.settings.apply()
        super().accept()


def mode_label(mode: str) -> str:
    return {
        "manual": "手动曲线",
        "horizontal_compare": "横向对比",
        "vertical_compare": "纵向对比",
    }.get(mode, mode)
