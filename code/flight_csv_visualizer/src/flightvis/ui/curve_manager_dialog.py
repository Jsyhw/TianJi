from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from flightvis.constants import LINE_STYLES
from flightvis.models.curve_override import CurveOverride
from flightvis.models.visibility import VisibilityState
from flightvis.plotting.plot_renderer import build_custom_display_curves, build_preset_display_curves
from flightvis.ui.widgets.color_button import ColorButton


class PresetCurveManagerDialog(QDialog):
    def __init__(self, plot_config, data_manager, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"曲线管理 - {plot_config.title}")
        self.plot_config = plot_config
        self.data_manager = data_manager
        self.project = project
        self.display_curves = []
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["显示", "别名", "X轴列", "Y轴列", "颜色", "线宽", "线型", "透明度"])

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        button_row = QHBoxLayout()
        all_on = QPushButton("全选")
        all_off = QPushButton("全不选")
        up = QPushButton("上移")
        down = QPushButton("下移")
        reset = QPushButton("恢复默认")
        button_row.addWidget(all_on)
        button_row.addWidget(all_off)
        button_row.addWidget(up)
        button_row.addWidget(down)
        button_row.addWidget(reset)
        button_row.addStretch(1)
        layout.addLayout(button_row)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        all_on.clicked.connect(lambda: self.set_all(True))
        all_off.clicked.connect(lambda: self.set_all(False))
        up.clicked.connect(lambda: self.move_selected(-1))
        down.clicked.connect(lambda: self.move_selected(1))
        reset.clicked.connect(self.reset_local)
        self.populate()

    def populate(self) -> None:
        self.display_curves = build_preset_display_curves(self.plot_config, self.data_manager.list_files())
        self.table.setRowCount(len(self.display_curves))
        for row, curve in enumerate(self.display_curves):
            self.table.setItem(row, 0, QTableWidgetItem())
            self.table.item(row, 0).setData(Qt.UserRole, curve.curve_id)
            check = QCheckBox()
            check.setChecked(curve.visible)
            self.table.setCellWidget(row, 0, check)
            self.table.setItem(row, 1, readonly_item(curve.label))
            self.table.setItem(row, 2, readonly_item(curve.x_column))
            self.table.setItem(row, 3, readonly_item(curve.y_column))
            color = ColorButton(curve.color or self.file_color(curve.file_id))
            self.table.setCellWidget(row, 4, color)
            width = QDoubleSpinBox()
            width.setRange(0.1, 10.0)
            width.setSingleStep(0.1)
            width.setValue(curve.line_width)
            self.table.setCellWidget(row, 5, width)
            style = QComboBox()
            style.addItems(LINE_STYLES)
            style.setCurrentText(curve.line_style)
            self.table.setCellWidget(row, 6, style)
            self.table.setCellWidget(row, 7, alpha_spin(curve.alpha))

    def file_color(self, file_id: str) -> str:
        config = self.data_manager.get_config(file_id)
        return config.color if config else "#1f77b4"

    def selected_row(self) -> int:
        row = self.table.currentRow()
        if row >= 0:
            return row
        selected = self.table.selectedItems()
        return selected[0].row() if selected else -1

    def move_selected(self, delta: int) -> None:
        row = self.selected_row()
        if row < 0:
            return
        new_row = row + delta
        if new_row < 0 or new_row >= len(self.display_curves):
            return
        self.capture_table_state()
        self.display_curves[row], self.display_curves[new_row] = self.display_curves[new_row], self.display_curves[row]
        self.populate_from_display_curves()
        self.table.selectRow(new_row)

    def capture_table_state(self) -> None:
        for row, curve in enumerate(self.display_curves):
            check = self.table.cellWidget(row, 0)
            color = self.table.cellWidget(row, 4)
            width = self.table.cellWidget(row, 5)
            style = self.table.cellWidget(row, 6)
            alpha = self.table.cellWidget(row, 7)
            curve.visible = check.isChecked()
            curve.use_file_color = False
            curve.color = color.color
            curve.line_width = float(width.value())
            curve.line_style = style.currentText()
            curve.alpha = float(alpha.value())

    def populate_from_display_curves(self) -> None:
        current = self.display_curves
        self.table.setRowCount(len(current))
        for row, curve in enumerate(current):
            check = QCheckBox()
            check.setChecked(curve.visible)
            self.table.setCellWidget(row, 0, check)
            self.table.setItem(row, 1, readonly_item(curve.label))
            self.table.setItem(row, 2, readonly_item(curve.x_column))
            self.table.setItem(row, 3, readonly_item(curve.y_column))
            self.table.setCellWidget(row, 4, ColorButton(curve.color or self.file_color(curve.file_id)))
            width = QDoubleSpinBox()
            width.setRange(0.1, 10.0)
            width.setSingleStep(0.1)
            width.setValue(curve.line_width)
            self.table.setCellWidget(row, 5, width)
            style = QComboBox()
            style.addItems(LINE_STYLES)
            style.setCurrentText(curve.line_style)
            self.table.setCellWidget(row, 6, style)
            self.table.setCellWidget(row, 7, alpha_spin(curve.alpha))

    def set_all(self, visible: bool) -> None:
        for row in range(self.table.rowCount()):
            check = self.table.cellWidget(row, 0)
            if isinstance(check, QCheckBox):
                check.setChecked(visible)

    def reset_local(self) -> None:
        self.plot_config.curve_visibility.clear()
        self.plot_config.curve_overrides.clear()
        self.plot_config.curve_order.clear()
        self.populate()

    def accept(self) -> None:
        self.capture_table_state()
        self.plot_config.curve_order = [curve.curve_id for curve in self.display_curves]
        self.plot_config.curve_overrides.clear()
        self.plot_config.curve_visibility.clear()
        for row, curve in enumerate(self.display_curves):
            version = self.project.next_visibility_version()
            visible = curve.visible
            self.plot_config.curve_visibility[curve.file_id] = VisibilityState(visible, version)
            self.plot_config.curve_overrides[curve.curve_id] = CurveOverride(
                visible=visible,
                visibility_version=version,
                use_file_color=False,
                color=curve.color,
                line_width=curve.line_width,
                line_style=curve.line_style,
                alpha=curve.alpha,
            )
        super().accept()


class CustomCurveManagerDialog(QDialog):
    def __init__(self, plot_config, data_manager, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"曲线管理 - {plot_config.title}")
        self.plot_config = plot_config
        self.data_manager = data_manager
        self.project = project
        self.display_curves = []
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(["显示", "名称", "来源", "文件", "X轴", "Y轴", "颜色", "线宽", "线型", "透明度"])

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        row = QHBoxLayout()
        delete = QPushButton("删除")
        up = QPushButton("上移")
        down = QPushButton("下移")
        row.addWidget(delete)
        row.addWidget(up)
        row.addWidget(down)
        row.addStretch(1)
        layout.addLayout(row)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        delete.clicked.connect(self.delete_selected)
        up.clicked.connect(lambda: self.move_selected(-1))
        down.clicked.connect(lambda: self.move_selected(1))
        self.populate()

    def populate(self) -> None:
        self.display_curves = build_custom_display_curves(self.plot_config, self.data_manager.list_files())
        self.populate_from_display_curves()

    def populate_from_display_curves(self) -> None:
        self.table.setRowCount(len(self.display_curves))
        for row, curve in enumerate(self.display_curves):
            check = QCheckBox()
            check.setChecked(curve.visible)
            self.table.setCellWidget(row, 0, check)
            name = QTableWidgetItem(curve.label)
            if curve.source != "manual":
                name.setFlags(name.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, name)
            self.table.setItem(row, 2, readonly_item(source_label(curve.source)))
            file_config = self.data_manager.get_config(curve.file_id)
            self.table.setItem(row, 3, readonly_item(file_config.alias if file_config else curve.file_id))
            self.table.setItem(row, 4, readonly_item(curve.x_column))
            self.table.setItem(row, 5, readonly_item(curve.y_column))
            color = curve.color or (file_config.color if file_config else "#1f77b4")
            self.table.setCellWidget(row, 6, ColorButton(color))
            width = QDoubleSpinBox()
            width.setRange(0.1, 10.0)
            width.setSingleStep(0.1)
            width.setValue(curve.line_width)
            self.table.setCellWidget(row, 7, width)
            style = QComboBox()
            style.addItems(LINE_STYLES)
            style.setCurrentText(curve.line_style)
            self.table.setCellWidget(row, 8, style)
            self.table.setCellWidget(row, 9, alpha_spin(curve.alpha))

    def selected_row(self) -> int:
        row = self.table.currentRow()
        if row >= 0:
            return row
        selected = self.table.selectedItems()
        return selected[0].row() if selected else -1

    def delete_selected(self) -> None:
        rows = sorted({item.row() for item in self.table.selectedItems()}, reverse=True)
        if not rows and self.selected_row() >= 0:
            rows = [self.selected_row()]
        for row in rows:
            curve = self.display_curves[row]
            if curve.source != "manual":
                continue
            self.plot_config.curves = [item for item in self.plot_config.curves if item.curve_id != curve.curve_id]
            self.plot_config.curve_overrides.pop(curve.curve_id, None)
            self.plot_config.curve_order = [item for item in self.plot_config.curve_order if item != curve.curve_id]
        self.populate()

    def move_selected(self, delta: int) -> None:
        row = self.selected_row()
        if row < 0:
            return
        new_row = row + delta
        if new_row < 0 or new_row >= len(self.display_curves):
            return
        self.capture_table_state()
        self.display_curves[row], self.display_curves[new_row] = self.display_curves[new_row], self.display_curves[row]
        self.populate_from_display_curves()
        self.table.selectRow(new_row)

    def capture_table_state(self) -> None:
        for row, curve in enumerate(self.display_curves):
            check = self.table.cellWidget(row, 0)
            color = self.table.cellWidget(row, 6)
            width = self.table.cellWidget(row, 7)
            style = self.table.cellWidget(row, 8)
            alpha = self.table.cellWidget(row, 9)
            curve.visible = check.isChecked()
            curve.color = color.color
            curve.use_file_color = False
            curve.line_width = float(width.value())
            curve.line_style = style.currentText()
            curve.alpha = float(alpha.value())
            if curve.source == "manual":
                curve.label = self.table.item(row, 1).text().strip() or curve.label

    def accept(self) -> None:
        self.capture_table_state()
        manual_by_id = {curve.curve_id: curve for curve in self.plot_config.curves}
        self.plot_config.curve_order = [curve.curve_id for curve in self.display_curves]
        for curve in self.display_curves:
            version = self.project.next_visibility_version()
            self.plot_config.curve_overrides[curve.curve_id] = CurveOverride(
                visible=curve.visible,
                visibility_version=version,
                use_file_color=curve.use_file_color,
                color=curve.color,
                line_width=curve.line_width,
                line_style=curve.line_style,
                alpha=curve.alpha,
            )
            if curve.source != "manual":
                self.plot_config.generated_curve_visibility[curve.curve_id] = curve.visible
                continue
            manual = manual_by_id.get(curve.curve_id)
            if not manual:
                continue
            manual.visible = curve.visible
            manual.visibility_version = version
            manual.label = curve.label
            manual.use_file_color = curve.use_file_color
            manual.color = curve.color
            manual.line_width = curve.line_width
            manual.line_style = curve.line_style
            manual.alpha = curve.alpha
        super().accept()


def readonly_item(value: str) -> QTableWidgetItem:
    item = QTableWidgetItem(value)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item


def alpha_spin(value: float = 1.0) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0.0, 1.0)
    spin.setDecimals(2)
    spin.setSingleStep(0.05)
    spin.setValue(value)
    return spin


def source_label(source: str) -> str:
    return {
        "manual": "手动添加",
        "horizontal_compare": "横向对比",
        "vertical_compare": "纵向对比",
        "preset": "默认图窗",
    }.get(source, source)
