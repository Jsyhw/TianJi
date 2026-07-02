from __future__ import annotations

from flightvis.plotting.plot_renderer import draw_preset_plot
from flightvis.ui.curve_manager_dialog import PresetCurveManagerDialog
from flightvis.ui.plot_cell_base import PlotCellBase
from flightvis.ui.preset_plot_settings_dialog import PresetPlotSettingsDialog


class PresetPlotCell(PlotCellBase):
    def __init__(self, plot_config, data_manager, project_manager, parent=None):
        super().__init__(plot_config, data_manager, project_manager, parent)
        self.curve_button.clicked.connect(self.open_curve_dialog)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.refresh()

    def refresh(self) -> None:
        ax = self.canvas.clear()
        draw_preset_plot(ax, self.plot_config, self.data_manager.list_files())
        self.canvas.draw_idle()

    def open_settings_dialog(self) -> None:
        dialog = PresetPlotSettingsDialog(self.plot_config, self)
        if dialog.exec():
            self.project_manager.mark_dirty()
            self.refresh()
            self.changed.emit()

    def open_curve_dialog(self) -> None:
        dialog = PresetCurveManagerDialog(self.plot_config, self.data_manager, self.project_manager.project, self)
        if dialog.exec():
            self.project_manager.mark_dirty()
            self.refresh()
            self.changed.emit()
