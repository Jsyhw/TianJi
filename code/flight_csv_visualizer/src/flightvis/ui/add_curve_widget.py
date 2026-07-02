from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)

from flightvis.models.curve_config import CurveConfig
from flightvis.ui.widgets.color_button import ColorButton


class AddCurveWidget(QWidget):
    def __init__(self, plot_config, data_manager, project, parent=None):
        super().__init__(parent)
        self.plot_config = plot_config
        self.data_manager = data_manager
        self.project = project
        self.file = QComboBox()
        self.x_col = QComboBox()
        self.y_col = QComboBox()
        self.label = QLineEdit()
        self.use_file_color = QCheckBox("使用文件颜色")
        self.use_file_color.setChecked(True)
        self.color = ColorButton()
        self.width = QDoubleSpinBox()
        self.width.setRange(0.1, 10.0)
        self.width.setValue(1.5)
        self.style = QComboBox()
        self.style.addItems(["-", "--", "-.", ":"])
        add = QPushButton("添加到当前图窗")
        layout = QFormLayout(self)
        layout.addRow("数据文件", self.file)
        layout.addRow("X轴列", self.x_col)
        layout.addRow("Y轴列", self.y_col)
        layout.addRow("曲线名称", self.label)
        layout.addRow("", self.use_file_color)
        layout.addRow("颜色", self.color)
        layout.addRow("线宽", self.width)
        layout.addRow("线型", self.style)
        layout.addRow("", add)
        self.file.currentIndexChanged.connect(self.populate_columns)
        self.y_col.currentTextChanged.connect(self.update_label)
        add.clicked.connect(self.add_curve)
        self.populate_files()

    def populate_files(self) -> None:
        self.file.clear()
        for data_file in self.data_manager.list_files():
            self.file.addItem(data_file.alias, data_file.file_id)
        self.populate_columns()

    def populate_columns(self) -> None:
        self.x_col.clear()
        self.y_col.clear()
        data_file = self.data_manager.get_file(self.file.currentData())
        columns = data_file.columns if data_file else []
        self.x_col.addItems(columns)
        self.y_col.addItems(columns)
        if "time" in columns:
            self.x_col.setCurrentText("time")
        self.update_label()

    def update_label(self) -> None:
        data_file = self.data_manager.get_file(self.file.currentData())
        alias = data_file.alias if data_file else "data"
        self.label.setText(f"{alias} / {self.y_col.currentText()}")

    def add_curve(self) -> None:
        file_id = self.file.currentData()
        if not file_id or not self.x_col.currentText() or not self.y_col.currentText():
            return
        curve = CurveConfig(
            curve_id=self.project.allocate_curve_id(),
            source="manual",
            file_id=file_id,
            x_column=self.x_col.currentText(),
            y_column=self.y_col.currentText(),
            label=self.label.text().strip() or f"{file_id} / {self.y_col.currentText()}",
            use_file_color=self.use_file_color.isChecked(),
            color=self.color.color,
            line_width=float(self.width.value()),
            line_style=self.style.currentText(),
        )
        self.plot_config.curves.append(curve)
