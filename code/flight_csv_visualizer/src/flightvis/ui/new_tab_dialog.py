from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QSpinBox, QVBoxLayout


class NewTabDialog(QDialog):
    def __init__(self, existing_names: set[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建自定义选项卡")
        self.existing_names = existing_names
        self.name = QLineEdit("自定义")
        self.rows = QSpinBox()
        self.rows.setRange(1, 5)
        self.rows.setValue(2)
        self.cols = QSpinBox()
        self.cols.setRange(1, 5)
        self.cols.setValue(2)
        form = QFormLayout()
        form.addRow("名称", self.name)
        form.addRow("行数", self.rows)
        form.addRow("列数", self.cols)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, int, int]:
        return self.name.text().strip(), self.rows.value(), self.cols.value()

    def accept(self) -> None:
        name, _, _ = self.values()
        if not name:
            QMessageBox.warning(self, "选项卡无效", "名称不能为空。")
            return
        if name in self.existing_names:
            QMessageBox.warning(self, "选项卡无效", "名称已存在。")
            return
        super().accept()
