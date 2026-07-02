from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from flightvis.constants import STANDARD_MAPPING_KEYS


class CompareModeWidget(QWidget):
    def __init__(self, plot_config, data_manager, parent=None):
        super().__init__(parent)
        self.plot_config = plot_config
        self.data_manager = data_manager

        self.manual = QRadioButton("手动曲线")
        self.horizontal = QRadioButton("横向对比")
        self.vertical = QRadioButton("纵向对比")

        self.h_compare_by = QComboBox()
        self.h_compare_by.addItem("按标准变量映射", "mapped_variable")
        self.h_compare_by.addItem("按实际列名", "actual_column")
        self.h_y = QComboBox()
        self.h_x_mode = QComboBox()
        self.h_x_mode.addItem("使用时间映射", "mapped_time")
        self.h_x_mode.addItem("指定实际列", "actual_column")
        self.h_x = QComboBox()
        self.h_files = QListWidget()
        self.h_auto = QCheckBox("自动包含后续加载文件")

        self.v_file = QComboBox()
        self.v_x = QComboBox()
        self.v_y = QListWidget()

        layout = QVBoxLayout(self)
        mode_box = QGroupBox("绘图模式")
        mode_layout = QHBoxLayout(mode_box)
        mode_layout.addWidget(self.manual)
        mode_layout.addWidget(self.horizontal)
        mode_layout.addWidget(self.vertical)
        layout.addWidget(mode_box)

        h_box = QGroupBox("横向对比")
        h_form = QFormLayout(h_box)
        h_form.addRow("对比方式", self.h_compare_by)
        h_form.addRow("Y变量/列", self.h_y)
        h_form.addRow("X轴模式", self.h_x_mode)
        h_form.addRow("X轴列", self.h_x)
        h_form.addRow("参与文件", self.h_files)
        h_form.addRow("", self.h_auto)
        layout.addWidget(h_box)

        v_box = QGroupBox("纵向对比")
        v_form = QFormLayout(v_box)
        v_form.addRow("数据文件", self.v_file)
        v_form.addRow("X轴列", self.v_x)
        v_form.addRow("Y轴列", self.v_y)
        layout.addWidget(v_box)
        self.v_file.currentIndexChanged.connect(self.populate_vertical_columns)
        self.populate()

    def populate(self) -> None:
        mode = self.plot_config.plot_mode
        self.manual.setChecked(mode == "manual")
        self.horizontal.setChecked(mode == "horizontal_compare")
        self.vertical.setChecked(mode == "vertical_compare")

        columns = sorted({col for data_file in self.data_manager.list_files() for col in data_file.columns})
        self.h_y.addItems(STANDARD_MAPPING_KEYS + columns)
        self.h_x.addItems(["time"] + columns)
        compare_index = self.h_compare_by.findData(self.plot_config.horizontal_compare.compare_by)
        if compare_index >= 0:
            self.h_compare_by.setCurrentIndex(compare_index)
        x_mode_index = self.h_x_mode.findData(self.plot_config.horizontal_compare.x_mode)
        if x_mode_index >= 0:
            self.h_x_mode.setCurrentIndex(x_mode_index)
        if self.plot_config.horizontal_compare.y_variable:
            self.h_y.setCurrentText(self.plot_config.horizontal_compare.y_variable)
        self.h_x.setCurrentText(self.plot_config.horizontal_compare.x_column)
        self.h_auto.setChecked(self.plot_config.horizontal_compare.auto_include_new_files)

        included = self.plot_config.horizontal_compare.included_file_ids
        for data_file in self.data_manager.list_files():
            item = QListWidgetItem(data_file.alias)
            item.setData(32, data_file.file_id)
            item.setCheckState(Qt.Checked if included == "all" or data_file.file_id in included else Qt.Unchecked)
            self.h_files.addItem(item)

        for data_file in self.data_manager.list_files():
            self.v_file.addItem(data_file.alias, data_file.file_id)
        if self.plot_config.vertical_compare.file_id:
            index = self.v_file.findData(self.plot_config.vertical_compare.file_id)
            if index >= 0:
                self.v_file.setCurrentIndex(index)
        self.populate_vertical_columns()

    def populate_vertical_columns(self) -> None:
        self.v_x.clear()
        self.v_y.clear()
        file_id = self.v_file.currentData()
        data_file = self.data_manager.get_file(file_id) if file_id else None
        columns = data_file.columns if data_file else []
        self.v_x.addItems(columns)
        if self.plot_config.vertical_compare.x_column in columns:
            self.v_x.setCurrentText(self.plot_config.vertical_compare.x_column)
        selected = set(self.plot_config.vertical_compare.y_columns)
        for column in columns:
            item = QListWidgetItem(column)
            item.setCheckState(Qt.Checked if column in selected else Qt.Unchecked)
            self.v_y.addItem(item)

    def apply(self) -> None:
        if self.horizontal.isChecked():
            self.plot_config.plot_mode = "horizontal_compare"
            self.plot_config.horizontal_compare.enabled = True
            self.plot_config.vertical_compare.enabled = False
        elif self.vertical.isChecked():
            self.plot_config.plot_mode = "vertical_compare"
            self.plot_config.horizontal_compare.enabled = False
            self.plot_config.vertical_compare.enabled = True
        else:
            self.plot_config.plot_mode = "manual"
            self.plot_config.horizontal_compare.enabled = False
            self.plot_config.vertical_compare.enabled = False

        h = self.plot_config.horizontal_compare
        h.compare_by = self.h_compare_by.currentData()
        h.y_variable = self.h_y.currentText() or None
        h.x_mode = self.h_x_mode.currentData()
        h.x_column = self.h_x.currentText() or "time"
        h.auto_include_new_files = self.h_auto.isChecked()
        included = []
        for index in range(self.h_files.count()):
            item = self.h_files.item(index)
            if item.checkState() == Qt.Checked:
                included.append(item.data(32))
        h.included_file_ids = "all" if len(included) == self.h_files.count() else included

        v = self.plot_config.vertical_compare
        v.file_id = self.v_file.currentData()
        v.x_column = self.v_x.currentText() or "time"
        y_columns = []
        for index in range(self.v_y.count()):
            item = self.v_y.item(index)
            if item.checkState() == Qt.Checked:
                y_columns.append(item.text())
        v.y_columns = y_columns
