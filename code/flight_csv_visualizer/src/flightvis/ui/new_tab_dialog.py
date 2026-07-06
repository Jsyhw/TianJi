from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from flightvis.models.tab_config import GridRegion
from flightvis.ui.advanced_grid_layout_dialog import AdvancedGridLayoutDialog


class NewTabDialog(QDialog):
    def __init__(self, existing_names: set[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建自定义选项卡")
        self.existing_names = existing_names
        self.advanced_layout: list[GridRegion] | None = None

        self.name = QLineEdit("自定义")
        self.rows = QSpinBox()
        self.rows.setRange(1, 6)
        self.rows.setValue(2)
        self.cols = QSpinBox()
        self.cols.setRange(1, 6)
        self.cols.setValue(2)
        self.advanced_button = QPushButton("高级")
        self.advanced_label = QLabel("固定网格")

        form = QFormLayout()
        form.addRow("名称", self.name)
        form.addRow("行数", self.rows)
        form.addRow("列数", self.cols)
        advanced_row = QHBoxLayout()
        advanced_row.addWidget(self.advanced_button)
        advanced_row.addWidget(self.advanced_label)
        advanced_row.addStretch(1)
        form.addRow("布局", advanced_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.rows.valueChanged.connect(self.clear_advanced_layout)
        self.cols.valueChanged.connect(self.clear_advanced_layout)
        self.advanced_button.clicked.connect(self.open_advanced_layout)

    def values(self) -> tuple[str, int, int, list[GridRegion] | None]:
        return self.name.text().strip(), self.rows.value(), self.cols.value(), self.advanced_layout

    def clear_advanced_layout(self) -> None:
        self.advanced_layout = None
        self.advanced_label.setText("固定网格")

    def open_advanced_layout(self) -> None:
        dialog = AdvancedGridLayoutDialog(max(2, self.rows.value()), max(2, self.cols.value()), self)
        if not dialog.exec():
            return
        self.rows.blockSignals(True)
        self.cols.blockSignals(True)
        self.rows.setValue(dialog.rows)
        self.cols.setValue(dialog.cols)
        self.rows.blockSignals(False)
        self.cols.blockSignals(False)
        self.advanced_layout = dialog.layout_regions()
        self.advanced_label.setText(f"高级布局：{len(self.advanced_layout)} 个图窗")

    def accept(self) -> None:
        name, _, _, _ = self.values()
        if not name:
            QMessageBox.warning(self, "选项卡无效", "名称不能为空。")
            return
        if name in self.existing_names:
            QMessageBox.warning(self, "选项卡无效", "名称已存在。")
            return
        super().accept()
