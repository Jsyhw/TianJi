from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout


class ImportFilesDialog(QDialog):
    def __init__(self, paths: list[str], default_aliases: list[str], existing_aliases: set[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("导入 CSV 文件")
        self.paths = paths
        self.existing_aliases = existing_aliases
        self.table = QTableWidget(len(paths), 3)
        self.table.setHorizontalHeaderLabels(["文件路径", "别名", "状态"])
        for row, path in enumerate(paths):
            self.table.setItem(row, 0, QTableWidgetItem(str(Path(path))))
            self.table.setItem(row, 1, QTableWidgetItem(default_aliases[row]))
            self.table.setItem(row, 2, QTableWidgetItem("就绪"))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(buttons)
        self.resize(760, 320)

    def aliases(self) -> list[str]:
        return [self.table.item(row, 1).text().strip() for row in range(self.table.rowCount())]

    def accept(self) -> None:
        aliases = self.aliases()
        if any(not alias for alias in aliases):
            QMessageBox.warning(self, "别名无效", "别名不能为空。")
            return
        if len(set(aliases)) != len(aliases):
            QMessageBox.warning(self, "别名无效", "新导入文件的别名不能重复。")
            return
        if set(aliases) & self.existing_aliases:
            QMessageBox.warning(self, "别名无效", "当前工程中已存在同名别名。")
            return
        super().accept()
