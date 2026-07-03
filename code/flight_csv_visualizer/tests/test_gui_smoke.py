import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTabWidget

from flightvis.constants import AXIS_LABEL_PRESETS
from flightvis.models.curve_config import CurveConfig
from flightvis.models.tab_config import create_custom_tab
from flightvis.plotting.plot_renderer import build_custom_display_curves, build_preset_display_curves
from flightvis.plotting.trajectory_renderer import build_trajectory_display_curves, draw_trajectory
from flightvis.resources import app_icon_path
from flightvis.ui.compare_mode_widget import HorizontalCompareSettingsWidget
from flightvis.ui.curve_manager_dialog import CustomCurveManagerDialog, PresetCurveManagerDialog
from flightvis.ui.custom_plot_settings_dialog import CustomPlotSettingsDialog
from flightvis.ui.legend_bar import LegendItemWidget
from flightvis.ui.main_window import MainWindow
from flightvis.ui.trajectory_curve_manager_dialog import TrajectoryCurveManagerDialog


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
    tabs = dialog.findChild(QTabWidget)
    assert dialog.windowTitle() == "自定义图窗设置"
    assert tabs.tabText(0) == "绘图设置"
    assert tabs.tabText(1) == "添加曲线"
    assert tabs.count() == 2
    assert dialog.settings.findChild(QTabWidget) is None
    assert dialog.settings.maximumHeight() != 30
    mode_row = dialog.settings.layout().itemAt(0).widget()
    assert mode_row.height() <= 30 or mode_row.maximumHeight() == 30
    assert dialog.settings.display.x_label.findText("速度 m/s") >= 0
    assert "角速度 deg/s" in AXIS_LABEL_PRESETS
    dialog.close()
    window.project_manager.dirty = False
    window.close()


def test_main_window_uses_tianji_icon(qapp):
    window = MainWindow()
    assert window.windowTitle() == "天玑 TianJi"
    assert app_icon_path().exists()
    assert not window.windowIcon().isNull()
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


def test_horizontal_compare_settings_uses_per_file_column_mapping(qapp):
    window = make_window_with_examples(qapp)
    tab_id = window.project.allocate_tab_id()
    window.project.tabs.append(create_custom_tab(tab_id, "横向", 1, 1))
    plot = window.project.tabs[1].plots[0]

    widget = HorizontalCompareSettingsWidget(plot, window.data_manager)
    widget.y_value.setCurrentText("vx")
    assert widget.files.rowCount() == 3
    for row in range(widget.files.rowCount()):
        assert widget.files.cellWidget(row, 0).isChecked()
        assert widget.files.cellWidget(row, 2).currentText()
    widget.files.cellWidget(0, 2).setCurrentText("vy")
    first_file_id = widget.files.item(0, 1).data(Qt.UserRole)
    widget.apply()

    assert plot.horizontal_compare.y_column_by_file[first_file_id] == "vy"
    curves = build_custom_display_curves(plot, window.data_manager.list_files())
    first_curve = next(curve for curve in curves if curve.file_id == first_file_id)
    assert first_curve.y_column == "vy"
    widget.close()
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


def test_custom_curve_manager_persists_generated_curve_style_and_order(qapp):
    window = make_window_with_examples(qapp)
    tab_id = window.project.allocate_tab_id()
    window.project.tabs.append(create_custom_tab(tab_id, "横向", 1, 1))
    plot = window.project.tabs[1].plots[0]
    plot.plot_mode = "horizontal_compare"
    plot.horizontal_compare.enabled = True
    plot.horizontal_compare.compare_by = "mapped_variable"
    plot.horizontal_compare.y_variable = "vx"
    plot.horizontal_compare.included_file_ids = "all"
    first_id = build_custom_display_curves(plot, window.data_manager.list_files())[0].curve_id

    dialog = CustomCurveManagerDialog(plot, window.data_manager, window.project, window)
    dialog.table.selectRow(0)
    dialog.table.cellWidget(0, 0).setChecked(False)
    dialog.table.cellWidget(0, 6).set_color("#abcdef")
    dialog.table.cellWidget(0, 7).setValue(3.2)
    dialog.table.cellWidget(0, 8).setCurrentText("--")
    dialog.table.cellWidget(0, 9).setValue(0.45)
    dialog.move_selected(1)
    dialog.accept()

    assert plot.curve_order[1] == first_id
    override = plot.curve_overrides[first_id]
    assert override.visible is False
    assert override.color == "#abcdef"
    assert override.line_width == pytest.approx(3.2)
    assert override.line_style == "--"
    assert override.alpha == pytest.approx(0.45)
    curves = build_custom_display_curves(plot, window.data_manager.list_files())
    moved = next(curve for curve in curves if curve.curve_id == first_id)
    assert moved.visible is False
    assert moved.color == "#abcdef"
    assert moved.alpha == pytest.approx(0.45)
    window.project_manager.dirty = False
    window.close()


def test_custom_curve_manager_persists_manual_curve_style(qapp):
    window = make_window_with_examples(qapp)
    tab_id = window.project.allocate_tab_id()
    window.project.tabs.append(create_custom_tab(tab_id, "手动", 1, 1))
    plot = window.project.tabs[1].plots[0]
    data_file = window.data_manager.list_files()[0]
    plot.curves.append(CurveConfig("manual_001", "manual", data_file.file_id, "time", "vx", "manual vx"))

    dialog = CustomCurveManagerDialog(plot, window.data_manager, window.project, window)
    dialog.table.cellWidget(0, 6).set_color("#fedcba")
    dialog.table.cellWidget(0, 7).setValue(2.6)
    dialog.table.cellWidget(0, 8).setCurrentText(":")
    dialog.table.cellWidget(0, 9).setValue(0.35)
    dialog.accept()

    curve = plot.curves[0]
    assert curve.use_file_color is False
    assert curve.color == "#fedcba"
    assert curve.line_width == pytest.approx(2.6)
    assert curve.line_style == ":"
    assert curve.alpha == pytest.approx(0.35)
    window.project_manager.dirty = False
    window.close()


def test_preset_curve_manager_supports_order_and_style(qapp):
    window = make_window_with_examples(qapp)
    plot = window.project.tabs[0].plots[0]
    first_id = build_preset_display_curves(plot, window.data_manager.list_files())[0].curve_id

    dialog = PresetCurveManagerDialog(plot, window.data_manager, window.project, window)
    dialog.table.selectRow(0)
    dialog.table.cellWidget(0, 4).set_color("#123456")
    dialog.table.cellWidget(0, 5).setValue(2.8)
    dialog.table.cellWidget(0, 6).setCurrentText("-.")
    dialog.table.cellWidget(0, 7).setValue(0.6)
    dialog.move_selected(1)
    dialog.accept()

    assert plot.curve_order[1] == first_id
    override = plot.curve_overrides[first_id]
    assert override.color == "#123456"
    assert override.line_width == pytest.approx(2.8)
    assert override.line_style == "-."
    assert override.alpha == pytest.approx(0.6)
    curves = build_preset_display_curves(plot, window.data_manager.list_files())
    moved = next(curve for curve in curves if curve.curve_id == first_id)
    assert moved.color == "#123456"
    assert moved.alpha == pytest.approx(0.6)
    window.project_manager.dirty = False
    window.close()


def test_csv_dialog_directory_uses_last_existing_folder(qapp):
    window = MainWindow()
    window.project.settings["last_csv_dir"] = str(EXAMPLE_DIR)
    assert window.csv_dialog_directory() == str(EXAMPLE_DIR)
    window.project.settings["last_csv_dir"] = str(EXAMPLE_DIR / "missing")
    assert Path(window.csv_dialog_directory()).exists()
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


def test_trajectory_equal_axis_keeps_data_bounds(qapp):
    from flightvis.plotting.mpl_canvas import MplCanvas

    window = make_window_with_examples(qapp)
    canvas = MplCanvas(projection="3d")
    config = dict(window.project.trajectory_view)
    config["equal_axis"] = True
    draw_trajectory(canvas.axes, window.data_manager.list_files(), config)
    x_span = canvas.axes.get_xlim()[1] - canvas.axes.get_xlim()[0]
    z_span = canvas.axes.get_zlim()[1] - canvas.axes.get_zlim()[0]
    assert z_span != pytest.approx(x_span)
    box_aspect = canvas.axes.get_box_aspect()
    assert box_aspect[0] != pytest.approx(box_aspect[2])
    window.project_manager.dirty = False
    window.close()


def test_trajectory_curve_manager_updates_style_alpha_and_equal_axis(qapp):
    window = make_window_with_examples(qapp)
    first_id = build_trajectory_display_curves(window.data_manager.list_files(), window.project.trajectory_view)[0].curve_id
    dialog = TrajectoryCurveManagerDialog(window.data_manager, window.project, window)
    assert dialog.table.rowCount() == 3
    dialog.equal_axis.setChecked(True)
    dialog.table.selectRow(0)
    dialog.table.cellWidget(0, 5).set_color("#654321")
    dialog.table.cellWidget(0, 6).setValue(3.4)
    dialog.table.cellWidget(0, 7).setCurrentText("--")
    dialog.table.cellWidget(0, 8).setValue(0.4)
    dialog.move_selected(1)
    dialog.accept()

    assert window.project.trajectory_view["equal_axis"] is True
    assert window.project.trajectory_view["curve_order"][1] == first_id
    override = window.project.trajectory_view["curve_overrides"][first_id]
    assert override["color"] == "#654321"
    assert override["line_width"] == pytest.approx(3.4)
    assert override["line_style"] == "--"
    assert override["alpha"] == pytest.approx(0.4)
    curves = build_trajectory_display_curves(window.data_manager.list_files(), window.project.trajectory_view)
    moved = next(curve for curve in curves if curve.curve_id == first_id)
    assert moved.alpha == pytest.approx(0.4)
    assert moved.color == "#654321"
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
