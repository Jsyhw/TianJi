from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QStyle, QToolButton, QVBoxLayout, QWidget

from flightvis.io.export_image import export_figure_png
from flightvis.plotting.mpl_canvas import MplCanvas


class PlotCellBase(QWidget):
    changed = Signal()
    selected = Signal(object)

    def __init__(self, plot_config, data_manager, project_manager, parent=None):
        super().__init__(parent)
        self.plot_config = plot_config
        self.data_manager = data_manager
        self.project_manager = project_manager
        self.canvas = MplCanvas(width=4, height=3)
        self.menu_button = QToolButton(self)
        self.menu_button.setText("▲")
        self.menu_button.setToolTip("图窗操作")
        self.menu_button.clicked.connect(self.toggle_action_panel)

        self.action_panel = QFrame(self)
        self.action_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.action_panel.setAutoFillBackground(True)
        panel_layout = QHBoxLayout(self.action_panel)
        panel_layout.setContentsMargins(3, 3, 3, 3)
        panel_layout.setSpacing(3)

        self.curve_button = self._make_action_button("曲线", QStyle.StandardPixmap.SP_FileDialogListView)
        self.settings_button = self._make_action_button("设置", QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.export_button = self._make_action_button("导出", QStyle.StandardPixmap.SP_DialogSaveButton)
        panel_layout.addWidget(self.curve_button)
        panel_layout.addWidget(self.settings_button)
        panel_layout.addWidget(self.export_button)
        self.action_panel.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.canvas, 1)

        self.export_button.clicked.connect(self.request_export)

    def _make_action_button(self, tooltip: str, icon: QStyle.StandardPixmap) -> QToolButton:
        button = QToolButton(self.action_panel)
        button.setIcon(self.style().standardIcon(icon))
        button.setToolTip(tooltip)
        button.setAutoRaise(True)
        return button

    def toggle_action_panel(self) -> None:
        self.action_panel.setVisible(not self.action_panel.isVisible())
        self.action_panel.raise_()
        self.menu_button.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_action_geometry()

    def update_action_geometry(self) -> None:
        side = max(14, min(30, min(self.width(), self.height()) // 8))
        button_side = max(18, min(34, min(self.width(), self.height()) // 7))
        margin = max(3, side // 5)
        self.menu_button.setFixedSize(side, side)
        self.menu_button.move(self.width() - side - margin, self.height() - side - margin)
        for button in [self.curve_button, self.settings_button, self.export_button]:
            button.setFixedSize(button_side, button_side)
            icon_side = max(12, int(button_side * 0.65))
            button.setIconSize(QSize(icon_side, icon_side))
        panel_width = button_side * 3 + margin * 4
        panel_height = button_side + margin * 2
        self.action_panel.setFixedSize(panel_width, panel_height)
        self.action_panel.move(
            max(margin, self.width() - panel_width - margin),
            max(margin, self.height() - panel_height - side - margin * 2),
        )
        self.action_panel.raise_()
        self.menu_button.raise_()

    def mousePressEvent(self, event):
        self.selected.emit(self)
        super().mousePressEvent(event)

    def refresh(self) -> None:
        raise NotImplementedError

    def export_png(self, path: str | Path) -> None:
        export_figure_png(self.canvas.figure, path)

    def request_export(self) -> None:
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        path, _ = QFileDialog.getSaveFileName(self, "导出图窗", "", "PNG 图像 (*.png)")
        if not path:
            return
        try:
            self.export_png(path)
        except Exception as exc:
            QMessageBox.critical(self, "导出失败", str(exc))
