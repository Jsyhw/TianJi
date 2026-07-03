from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from flightvis.io.export_image import export_figure_png
from flightvis.plotting.mpl_canvas import MplCanvas
from flightvis.plotting.trajectory_renderer import draw_trajectory
from flightvis.ui.trajectory_curve_manager_dialog import TrajectoryCurveManagerDialog


class TrajectoryView(QWidget):
    def __init__(self, data_manager, project_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.project_manager = project_manager
        self.canvas = MplCanvas(width=5, height=5, projection="3d")
        self.curve_button = QPushButton("曲线管理")
        self.curve_button.setFixedHeight(26)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        toolbar = QHBoxLayout()
        toolbar.addStretch(1)
        toolbar.addWidget(self.curve_button)
        layout.addLayout(toolbar)
        layout.addWidget(self.canvas)
        self.curve_button.clicked.connect(self.open_curve_dialog)
        self.refresh()

    def refresh(self) -> None:
        ax = self.canvas.clear_3d()
        draw_trajectory(ax, self.data_manager.list_files(), self.project_manager.project.trajectory_view)
        self.canvas.draw_idle()

    def export_png(self, path: str | Path) -> None:
        export_figure_png(self.canvas.figure, path)

    def open_curve_dialog(self) -> None:
        dialog = TrajectoryCurveManagerDialog(self.data_manager, self.project_manager.project, self)
        if dialog.exec():
            self.project_manager.mark_dirty()
            self.refresh()
