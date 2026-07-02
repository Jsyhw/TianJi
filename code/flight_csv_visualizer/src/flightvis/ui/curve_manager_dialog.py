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

from flightvis.models.visibility import VisibilityState
from flightvis.plotting.plot_renderer import build_custom_display_curves
from flightvis.ui.widgets.color_button import ColorButton


class PresetCurveManagerDialog(QDialog):
    def __init__(self, plot_config, data_manager, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"曲线管理 - {plot_config.title}")
        self.plot_config = plot_config
        self.data_manager = data_manager
        self.project = project
        self.checks: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["显示", "别名", "X轴列", "Y轴列"])
        layout.addWidget(self.table)
        button_row = QHBoxLayout()
        all_on = QPushButton("全选")
        all_off = QPushButton("全不选")
        reset = QPushButton("恢复默认")
        button_row.addWidget(all_on)
        button_row.addWidget(all_off)
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
        reset.clicked.connect(self.reset_local)
        self.populate()

    def populate(self) -> None:
        rows = []
        for data_file in self.data_manager.list_files():
            x_col = data_file.mapped_column("time") or ""
            y_col = data_file.mapped_column(self.plot_config.preset_variable) or ""
            if not x_col or not y_col:
                continue
            rows.append((data_file, x_col, y_col))
        self.table.setRowCount(len(rows))
        for row, (data_file, x_col, y_col) in enumerate(rows):
            state = self.plot_config.curve_visibility.get(data_file.file_id)
            visible = state.visible if state else data_file.config.visible
            check = QCheckBox()
            check.setChecked(visible)
            self.checks[data_file.file_id] = check
            self.table.setCellWidget(row, 0, check)
            self.table.setItem(row, 1, QTableWidgetItem(data_file.alias))
            self.table.setItem(row, 2, QTableWidgetItem(x_col))
            self.table.setItem(row, 3, QTableWidgetItem(y_col))

    def set_all(self, visible: bool) -> None:
        for check in self.checks.values():
            check.setChecked(visible)

    def reset_local(self) -> None:
        self.plot_config.curve_visibility.clear()
        for file_id, check in self.checks.items():
            config = self.data_manager.get_config(file_id)
            check.setChecked(config.visible if config else True)

    def accept(self) -> None:
        for file_id, check in self.checks.items():
            version = self.project.next_visibility_version()
            self.plot_config.curve_visibility[file_id] = VisibilityState(check.isChecked(), version)
        super().accept()


class CustomCurveManagerDialog(QDialog):
    def __init__(self, plot_config, data_manager, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"曲线管理 - {plot_config.title}")
        self.plot_config = plot_config
        self.data_manager = data_manager
        self.project = project
        self.display_curves = []
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["显示", "名称", "来源", "文件", "X轴", "Y轴", "线宽", "线型"])

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
        self.table.setRowCount(len(self.display_curves))
        for row, curve in enumerate(self.display_curves):
            is_manual = curve.source == "manual"
            check = QCheckBox()
            check.setChecked(curve.visible)
            self.table.setCellWidget(row, 0, check)
            self.table.setItem(row, 1, QTableWidgetItem(curve.label))
            self.table.setItem(row, 2, QTableWidgetItem(source_label(curve.source)))
            file_config = self.data_manager.get_config(curve.file_id)
            self.table.setItem(row, 3, QTableWidgetItem(file_config.alias if file_config else curve.file_id))
            self.table.setItem(row, 4, QTableWidgetItem(curve.x_column))
            self.table.setItem(row, 5, QTableWidgetItem(curve.y_column))
            width = QDoubleSpinBox()
            width.setRange(0.1, 10.0)
            width.setValue(curve.line_width)
            width.setEnabled(is_manual)
            self.table.setCellWidget(row, 6, width)
            style = QComboBox()
            style.addItems(["-", "--", "-.", ":"])
            style.setCurrentText(curve.line_style)
            style.setEnabled(is_manual)
            self.table.setCellWidget(row, 7, style)
            if not is_manual:
                for col in [1, 2, 3, 4, 5]:
                    item = self.table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def delete_selected(self) -> None:
        rows = sorted({item.row() for item in self.table.selectedItems()}, reverse=True)
        for row in rows:
            curve = self.display_curves[row]
            if curve.source != "manual":
                continue
            self.plot_config.curves = [item for item in self.plot_config.curves if item.curve_id != curve.curve_id]
        self.populate()

    def move_selected(self, delta: int) -> None:
        rows = sorted({item.row() for item in self.table.selectedItems()})
        if len(rows) != 1:
            return
        row = rows[0]
        curve = self.display_curves[row]
        if curve.source != "manual":
            return
        manual_curves = self.plot_config.curves
        manual_index = next((index for index, item in enumerate(manual_curves) if item.curve_id == curve.curve_id), -1)
        if manual_index < 0:
            return
        new_manual_index = manual_index + delta
        if new_manual_index < 0 or new_manual_index >= len(manual_curves):
            return
        manual_curves[manual_index], manual_curves[new_manual_index] = manual_curves[new_manual_index], manual_curves[manual_index]
        self.populate()
        new_row = next((index for index, item in enumerate(self.display_curves) if item.curve_id == curve.curve_id), row)
        self.table.selectRow(new_row)

    def accept(self) -> None:
        manual_by_id = {curve.curve_id: curve for curve in self.plot_config.curves}
        for row, curve in enumerate(self.display_curves):
            check = self.table.cellWidget(row, 0)
            width = self.table.cellWidget(row, 6)
            style = self.table.cellWidget(row, 7)
            if curve.source == "manual":
                manual = manual_by_id.get(curve.curve_id)
                if not manual:
                    continue
                manual.visible = check.isChecked()
                manual.visibility_version = self.project.next_visibility_version()
                manual.label = self.table.item(row, 1).text()
                manual.line_width = float(width.value())
                manual.line_style = style.currentText()
            else:
                self.plot_config.generated_curve_visibility[curve.curve_id] = check.isChecked()
        super().accept()


def source_label(source: str) -> str:
    return {
        "manual": "手动添加",
        "horizontal_compare": "横向对比",
        "vertical_compare": "纵向对比",
    }.get(source, source)
