from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from flightvis.ui.column_mapping_dialog import ColumnMappingDialog
from flightvis.ui.widgets.color_button import ColorButton


class FileManagerDialog(QDialog):
    def __init__(self, data_manager, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据文件管理")
        self.data_manager = data_manager
        self.project = project
        self.removed: list[str] = []
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["显示", "别名", "颜色", "行数", "路径", "列映射", "移除"])
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.populate()
        self.resize(980, 360)

    def populate(self) -> None:
        files = self.data_manager.list_files()
        self.table.setRowCount(len(files))
        for row, data_file in enumerate(files):
            check = QCheckBox()
            check.setChecked(data_file.config.visible)
            self.table.setCellWidget(row, 0, check)
            self.table.setItem(row, 1, QTableWidgetItem(data_file.alias))
            color = ColorButton(data_file.config.color)
            self.table.setCellWidget(row, 2, color)
            self.table.setItem(row, 3, QTableWidgetItem(str(data_file.row_count)))
            self.table.setItem(row, 4, QTableWidgetItem(data_file.config.path))
            mapping_button = QPushButton("编辑")
            mapping_button.clicked.connect(lambda _=False, df=data_file: self.edit_mapping(df))
            self.table.setCellWidget(row, 5, mapping_button)
            remove_button = QPushButton("移除")
            remove_button.clicked.connect(lambda _=False, fid=data_file.file_id: self.remove_file(fid))
            self.table.setCellWidget(row, 6, remove_button)

    def edit_mapping(self, data_file) -> None:
        dialog = ColumnMappingDialog(data_file.columns, data_file.config.column_mapping, f"列映射 - {data_file.alias}", self)
        if dialog.exec():
            data_file.config.column_mapping = dialog.mapping()

    def remove_file(self, file_id: str) -> None:
        self.removed.append(file_id)
        self.data_manager.remove_file(file_id)
        self.populate()

    def accept(self) -> None:
        for row, data_file in enumerate(self.data_manager.list_files()):
            check = self.table.cellWidget(row, 0)
            color = self.table.cellWidget(row, 2)
            alias = self.table.item(row, 1).text().strip()
            self.data_manager.rename_file(data_file.file_id, alias)
            data_file.config.color = color.color
            visible = check.isChecked()
            if data_file.config.visible != visible:
                data_file.config.visible = visible
                data_file.config.visibility_version = self.project.next_visibility_version()
        super().accept()
