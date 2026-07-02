import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from flightvis.models.tab_config import create_custom_tab
from flightvis.plotting.plot_renderer import build_custom_display_curves
from flightvis.plotting.trajectory_renderer import draw_trajectory
from flightvis.ui.curve_manager_dialog import CustomCurveManagerDialog
from flightvis.ui.custom_plot_settings_dialog import CustomPlotSettingsDialog
from flightvis.ui.legend_bar import LegendItemWidget
from flightvis.ui.main_window import MainWindow


EXAMPLE_DIR = Path(__file__).resolve().parents[3] / "example"


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def make_window_with_examples(qapp):
    window = MainWindow()
    for name in ["exampe-1.csv", "example-2.csv", "example-3.csv"]:
        window.data_manager.add_csv(EXAMPLE_DIR / name)
    window.refresh_all_views()
    return window


def test_custom_plot_settings_dialog_constructs(qapp):
    window = make_window_with_examples(qapp)
    tab_id = window.project.allocate_tab_id()
    window.project.tabs.append(create_custom_tab(tab_id, "测试页", 1, 1))
    window.refresh_all_views()
    cell = window.tab_widgets[1].cells[0]
    dialog = CustomPlotSettingsDialog(cell.plot_config, window.data_manager, window.project, window)
    assert dialog.windowTitle() == "自定义图窗设置"
    dialog.close()
    window.project_manager.dirty = False
    window.close()


def test_tab_add_button_and_custom_tab_close(qapp):
    window = MainWindow()
    assert window.tabs.cornerWidget(Qt.TopRightCorner) is window.add_tab_button
    assert window.tabs.count() == 1
    tab_id = window.project.allocate_tab_id()
    window.project.tabs.append(create_custom_tab(tab_id, "测试页", 1, 1))
    window.refresh_all_views()
    assert window.tabs.count() == 2
    window.remove_tab_at(1)
    assert window.tabs.count() == 1
    assert window.project.tabs[0].name == "基本状态量"
    window.project_manager.dirty = False
    window.close()


def test_refresh_preserves_current_custom_tab(qapp):
    window = make_window_with_examples(qapp)
    tab_id = window.project.allocate_tab_id()
    window.project.tabs.append(create_custom_tab(tab_id, "测试页", 1, 1))
    window.refresh_all_views(preferred_tab_id=tab_id)
    assert window.tabs.currentIndex() == 1
    window.refresh_all_views()
    assert window.tabs.currentIndex() == 1
    window.project_manager.dirty = False
    window.close()


def test_horizontal_generated_curves_show_in_manager(qapp):
    window = make_window_with_examples(qapp)
    tab_id = window.project.allocate_tab_id()
    window.project.tabs.append(create_custom_tab(tab_id, "横向", 1, 1))
    plot = window.project.tabs[1].plots[0]
    plot.plot_mode = "horizontal_compare"
    plot.horizontal_compare.enabled = True
    plot.horizontal_compare.compare_by = "mapped_variable"
    plot.horizontal_compare.y_variable = "vx"
    plot.horizontal_compare.included_file_ids = "all"
    curves = build_custom_display_curves(plot, window.data_manager.list_files())
    dialog = CustomCurveManagerDialog(plot, window.data_manager, window.project, window)
    assert len(curves) == 3
    assert dialog.table.rowCount() == 3
    dialog.close()
    window.project_manager.dirty = False
    window.close()


def test_vertical_generated_curves_show_in_manager(qapp):
    window = make_window_with_examples(qapp)
    tab_id = window.project.allocate_tab_id()
    window.project.tabs.append(create_custom_tab(tab_id, "纵向", 1, 1))
    plot = window.project.tabs[1].plots[0]
    first_file = window.data_manager.list_files()[0]
    plot.plot_mode = "vertical_compare"
    plot.vertical_compare.enabled = True
    plot.vertical_compare.file_id = first_file.file_id
    plot.vertical_compare.x_column = "time"
    plot.vertical_compare.y_columns = ["T_f", "T_in", "T_a"]
    curves = build_custom_display_curves(plot, window.data_manager.list_files())
    dialog = CustomCurveManagerDialog(plot, window.data_manager, window.project, window)
    assert len(curves) == 3
    assert dialog.table.rowCount() == 3
    dialog.close()
    window.project_manager.dirty = False
    window.close()


def test_plot_cell_uses_corner_menu_instead_of_fixed_button_row(qapp):
    window = make_window_with_examples(qapp)
    cell = window.tab_widgets[0].cells[0]
    assert cell.menu_button.toolTip() == "图窗操作"
    assert cell.action_panel.isHidden()
    assert cell.curve_button.toolTip() == "曲线"
    window.project_manager.dirty = False
    window.close()


def test_trajectory_uses_per_axis_bounds(qapp):
    from flightvis.plotting.mpl_canvas import MplCanvas

    window = make_window_with_examples(qapp)
    canvas = MplCanvas(projection="3d")
    config = dict(window.project.trajectory_view)
    config["equal_axis"] = False
    draw_trajectory(canvas.axes, window.data_manager.list_files(), config)
    x_span = canvas.axes.get_xlim()[1] - canvas.axes.get_xlim()[0]
    z_span = canvas.axes.get_zlim()[1] - canvas.axes.get_zlim()[0]
    assert z_span != pytest.approx(x_span)
    window.project_manager.dirty = False
    window.close()


def test_legend_item_uses_checkbox(qapp):
    window = make_window_with_examples(qapp)
    data_file = window.data_manager.list_files()[0]
    item = LegendItemWidget(data_file)
    assert item.visible_check.isChecked() is True
    assert item.label.text() == data_file.alias
    item.visible_check.setChecked(False)
    assert item.visible_check.isChecked() is False
    item.close()
    window.project_manager.dirty = False
    window.close()
