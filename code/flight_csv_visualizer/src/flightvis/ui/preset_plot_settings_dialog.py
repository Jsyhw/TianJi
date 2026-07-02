from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from flightvis.ui.display_settings_widget import DisplaySettingsWidget


class PresetPlotSettingsDialog(QDialog):
    def __init__(self, plot_config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("预设图窗设置")
        self.plot_config = plot_config
        self.settings = DisplaySettingsWidget(
            plot_config.display,
            lambda: plot_config.title,
            lambda value: setattr(plot_config, "title", value),
        )
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.settings)
        layout.addWidget(buttons)

    def accept(self) -> None:
        self.settings.apply()
        super().accept()
