from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QScrollArea, QWidget

from flightvis.ui.custom_plot_cell import CustomPlotCell
from flightvis.ui.preset_plot_cell import PresetPlotCell


class TabGridWidget(QScrollArea):
    plot_selected = Signal(object)
    changed = Signal()

    def __init__(self, tab_config, data_manager, project_manager, parent=None):
        super().__init__(parent)
        self.tab_config = tab_config
        self.data_manager = data_manager
        self.project_manager = project_manager
        self.cells = []
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(6)
        self.setWidgetResizable(True)
        self.setWidget(self.container)
        self.rebuild()

    def rebuild(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.cells = []
        for plot in self.tab_config.plots:
            if plot.plot_type == "preset":
                cell = PresetPlotCell(plot, self.data_manager, self.project_manager)
            else:
                cell = CustomPlotCell(plot, self.data_manager, self.project_manager)
            cell.changed.connect(self.changed.emit)
            cell.selected.connect(self.plot_selected.emit)
            self.grid.addWidget(cell, plot.row, plot.col)
            self.cells.append(cell)

    def refresh(self) -> None:
        for cell in self.cells:
            cell.refresh()
