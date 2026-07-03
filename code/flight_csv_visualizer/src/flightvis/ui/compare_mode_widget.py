from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from flightvis.constants import STANDARD_MAPPING_KEYS


class HorizontalCompareSettingsWidget(QWidget):
    def __init__(self, plot_config, data_manager, parent=None):
        super().__init__(parent)
        self.plot_config = plot_config
        self.data_manager = data_manager

        self.y_value = QComboBox()
        self.x_mode = QComboBox()
        self.x_mode.addItem("使用时间映射", "mapped_time")
        self.x_mode.addItem("指定实际列", "actual_column")
        self.x_value = QComboBox()
        self.files = QTableWidget(0, 3)
        self.files.setHorizontalHeaderLabels(["参与", "数据文件", "Y轴列"])
        self.auto_include = QCheckBox("自动包含后续加载文件")
        self.use_saved_mapping = True

        layout = QFormLayout(self)
        layout.addRow("Y轴目标变量", self.y_value)
        layout.addRow("X轴模式", self.x_mode)
        layout.addRow("X轴列", self.x_value)
        layout.addRow("参与文件与列映射", self.files)
        layout.addRow("", self.auto_include)
        self.populate()
        self.y_value.currentTextChanged.connect(self.on_y_target_changed)

    def populate(self) -> None:
        config = self.plot_config.horizontal_compare
        columns = sorted({col for data_file in self.data_manager.list_files() for col in data_file.columns})
        self.y_value.addItems(STANDARD_MAPPING_KEYS + columns)
        self.x_value.addItems(["time"] + columns)
        x_mode_index = self.x_mode.findData(config.x_mode)
        if x_mode_index >= 0:
            self.x_mode.setCurrentIndex(x_mode_index)
        if config.y_variable:
            self.y_value.setCurrentText(config.y_variable)
        self.x_value.setCurrentText(config.x_column)
        self.auto_include.setChecked(config.auto_include_new_files)
        self.populate_file_mapping()

    def on_y_target_changed(self) -> None:
        self.use_saved_mapping = False
        self.populate_file_mapping()

    def populate_file_mapping(self) -> None:
        config = self.plot_config.horizontal_compare
        target = self.y_value.currentText()
        included = config.included_file_ids
        data_files = self.data_manager.list_files()
        self.files.setRowCount(len(data_files))
        for row, data_file in enumerate(data_files):
            selected_col = self.selected_y_column(data_file, target)
            participate = bool(selected_col) and (included == "all" or data_file.file_id in included)
            check = QCheckBox()
            check.setChecked(participate)
            self.files.setCellWidget(row, 0, check)
            file_item = QTableWidgetItem(data_file.alias)
            file_item.setData(Qt.UserRole, data_file.file_id)
            file_item.setFlags(file_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files.setItem(row, 1, file_item)
            column = QComboBox()
            column.addItem("不参与", "")
            column.addItems(data_file.columns)
            if selected_col:
                column.setCurrentText(selected_col)
            else:
                column.setCurrentIndex(0)
            column.currentTextChanged.connect(lambda text, check=check: check.setChecked(bool(text and text != "不参与")))
            self.files.setCellWidget(row, 2, column)
        self.files.resizeColumnsToContents()

    def selected_y_column(self, data_file, target: str) -> str:
        explicit = self.plot_config.horizontal_compare.y_column_by_file.get(data_file.file_id)
        if self.use_saved_mapping and explicit in data_file.columns:
            return explicit
        mapped = data_file.mapped_column(target)
        if mapped in data_file.columns:
            return mapped
        if target in data_file.columns:
            return target
        return ""

    def apply(self) -> None:
        self.plot_config.plot_mode = "horizontal_compare"
        self.plot_config.horizontal_compare.enabled = True
        self.plot_config.vertical_compare.enabled = False

        config = self.plot_config.horizontal_compare
        config.compare_by = "actual_column"
        config.y_variable = self.y_value.currentText() or None
        config.x_mode = self.x_mode.currentData()
        config.x_column = self.x_value.currentText() or "time"
        config.auto_include_new_files = self.auto_include.isChecked()
        included = []
        mapping = {}
        auto_matched = 0
        for row in range(self.files.rowCount()):
            item = self.files.item(row, 1)
            check = self.files.cellWidget(row, 0)
            column = self.files.cellWidget(row, 2)
            file_id = item.data(Qt.UserRole)
            y_col = column.currentData() if column.currentData() is not None else column.currentText()
            if y_col:
                auto_matched += 1
            if check.isChecked() and y_col:
                included.append(file_id)
                mapping[file_id] = y_col
        config.included_file_ids = "all" if self.auto_include.isChecked() and len(included) == auto_matched else included
        config.y_column_by_file = mapping


class VerticalCompareSettingsWidget(QWidget):
    def __init__(self, plot_config, data_manager, parent=None):
        super().__init__(parent)
        self.plot_config = plot_config
        self.data_manager = data_manager

        self.file = QComboBox()
        self.x_value = QComboBox()
        self.y_values = QListWidget()

        layout = QFormLayout(self)
        layout.addRow("数据文件", self.file)
        layout.addRow("X轴列", self.x_value)
        layout.addRow("Y轴列", self.y_values)
        self.file.currentIndexChanged.connect(self.populate_columns)
        self.populate()

    def populate(self) -> None:
        for data_file in self.data_manager.list_files():
            self.file.addItem(data_file.alias, data_file.file_id)
        config = self.plot_config.vertical_compare
        if config.file_id:
            index = self.file.findData(config.file_id)
            if index >= 0:
                self.file.setCurrentIndex(index)
        self.populate_columns()

    def populate_columns(self) -> None:
        self.x_value.clear()
        self.y_values.clear()
        file_id = self.file.currentData()
        data_file = self.data_manager.get_file(file_id) if file_id else None
        columns = data_file.columns if data_file else []
        self.x_value.addItems(columns)
        config = self.plot_config.vertical_compare
        if config.x_column in columns:
            self.x_value.setCurrentText(config.x_column)
        selected = set(config.y_columns)
        for column in columns:
            item = QListWidgetItem(column)
            item.setCheckState(Qt.Checked if column in selected else Qt.Unchecked)
            self.y_values.addItem(item)

    def apply(self) -> None:
        self.plot_config.plot_mode = "vertical_compare"
        self.plot_config.horizontal_compare.enabled = False
        self.plot_config.vertical_compare.enabled = True

        config = self.plot_config.vertical_compare
        config.file_id = self.file.currentData()
        config.x_column = self.x_value.currentText() or "time"
        y_columns = []
        for index in range(self.y_values.count()):
            item = self.y_values.item(index)
            if item.checkState() == Qt.Checked:
                y_columns.append(item.text())
        config.y_columns = y_columns


class HorizontalCompareDialog(QDialog):
    def __init__(self, plot_config, data_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("横向对比设置")
        self.settings = HorizontalCompareSettingsWidget(plot_config, data_manager)
        self._setup_layout()

    def _setup_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(self.settings)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.resize(520, 520)

    def accept(self) -> None:
        self.settings.apply()
        super().accept()


class VerticalCompareDialog(QDialog):
    def __init__(self, plot_config, data_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("纵向对比设置")
        self.settings = VerticalCompareSettingsWidget(plot_config, data_manager)
        self._setup_layout()

    def _setup_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(self.settings)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.resize(480, 520)

    def accept(self) -> None:
        self.settings.apply()
        super().accept()
