from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTabWidget, QVBoxLayout

from flightvis.ui.add_curve_widget import AddCurveWidget
from flightvis.ui.compare_mode_widget import CompareModeWidget
from flightvis.ui.display_settings_widget import DisplaySettingsWidget


class CustomPlotSettingsDialog(QDialog):
    def __init__(self, plot_config, data_manager, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义图窗设置")
        self.compare = CompareModeWidget(plot_config, data_manager)
        self.display = DisplaySettingsWidget(
            plot_config.display,
            lambda: plot_config.title,
            lambda value: setattr(plot_config, "title", value),
        )
        self.add_curve = AddCurveWidget(plot_config, data_manager, project)
        tabs = QTabWidget()
        tabs.addTab(self.compare, "绘图模式")
        tabs.addTab(self.display, "绘图细节")
        tabs.addTab(self.add_curve, "添加曲线")
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(buttons)
        self.resize(640, 620)

    def accept(self) -> None:
        self.compare.apply()
        self.display.apply()
        super().accept()
