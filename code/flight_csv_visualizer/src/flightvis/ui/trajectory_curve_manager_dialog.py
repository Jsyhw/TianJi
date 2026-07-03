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
    QVBoxLayout,
)

from flightvis.constants import LINE_STYLES
from flightvis.models.curve_override import CurveOverride
from flightvis.plotting.trajectory_renderer import build_trajectory_display_curves
from flightvis.ui.curve_manager_dialog import alpha_spin, readonly_item
from flightvis.ui.widgets.color_button import ColorButton


class TrajectoryCurveManagerDialog(QDialog):
    def __init__(self, data_manager, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("三维轨迹曲线管理")
        self.data_manager = data_manager
        self.project = project
        self.config = project.trajectory_view
        self.display_curves = []
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["显示", "别名", "X轴列", "Y轴列", "Z轴列", "颜色", "线宽", "线型", "透明度"])
        self.equal_axis = QCheckBox("各坐标轴等比例")
        self.equal_axis.setChecked(bool(self.config.get("equal_axis", False)))

        layout = QVBoxLayout(self)
        layout.addWidget(self.equal_axis)
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
        self.resize(760, 440)
        self.populate()

    def populate(self) -> None:
        self.display_curves = build_trajectory_display_curves(self.data_manager.list_files(), self.config)
        self.populate_from_display_curves()

    def populate_from_display_curves(self) -> None:
        self.table.setRowCount(len(self.display_curves))
        for row, curve in enumerate(self.display_curves):
            data_file = self.data_manager.get_file(curve.file_id)
            z_col = data_file.mapped_column("z") if data_file else ""
            check = QCheckBox()
            check.setChecked(curve.visible)
            self.table.setCellWidget(row, 0, check)
            self.table.setItem(row, 1, readonly_item(curve.label))
            self.table.setItem(row, 2, readonly_item(curve.x_column))
            self.table.setItem(row, 3, readonly_item(curve.y_column))
            self.table.setItem(row, 4, readonly_item(z_col or ""))
            color = curve.color or (data_file.config.color if data_file else "#1f77b4")
            self.table.setCellWidget(row, 5, ColorButton(color))
            width = QDoubleSpinBox()
            width.setRange(0.1, 10.0)
            width.setSingleStep(0.1)
            width.setValue(curve.line_width)
            self.table.setCellWidget(row, 6, width)
            style = QComboBox()
            style.addItems(LINE_STYLES)
            style.setCurrentText(curve.line_style)
            self.table.setCellWidget(row, 7, style)
            self.table.setCellWidget(row, 8, alpha_spin(curve.alpha))

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
            color = self.table.cellWidget(row, 5)
            width = self.table.cellWidget(row, 6)
            style = self.table.cellWidget(row, 7)
            alpha = self.table.cellWidget(row, 8)
            curve.visible = check.isChecked()
            curve.use_file_color = False
            curve.color = color.color
            curve.line_width = float(width.value())
            curve.line_style = style.currentText()
            curve.alpha = float(alpha.value())

    def set_all(self, visible: bool) -> None:
        for row in range(self.table.rowCount()):
            check = self.table.cellWidget(row, 0)
            if isinstance(check, QCheckBox):
                check.setChecked(visible)

    def reset_local(self) -> None:
        self.config.pop("curve_overrides", None)
        self.config.pop("curve_order", None)
        self.equal_axis.setChecked(False)
        self.populate()

    def accept(self) -> None:
        self.capture_table_state()
        self.config["equal_axis"] = self.equal_axis.isChecked()
        self.config["curve_order"] = [curve.curve_id for curve in self.display_curves]
        overrides = {}
        for curve in self.display_curves:
            overrides[curve.curve_id] = CurveOverride(
                visible=curve.visible,
                visibility_version=self.project.next_visibility_version(),
                use_file_color=curve.use_file_color,
                color=curve.color,
                line_width=curve.line_width,
                line_style=curve.line_style,
                alpha=curve.alpha,
            ).to_dict()
        self.config["curve_overrides"] = overrides
        super().accept()
