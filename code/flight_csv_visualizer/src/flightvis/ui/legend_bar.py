from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QInputDialog, QLabel, QScrollArea, QWidget

from flightvis.ui.widgets.color_button import ColorButton


class LegendItemWidget(QWidget):
    toggled = Signal(str, bool)
    alias_changed = Signal(str, str)
    color_changed = Signal(str, str)

    def __init__(self, data_file, parent=None):
        super().__init__(parent)
        self.data_file = data_file
        self.color = ColorButton(data_file.config.color)
        self.label = QLabel()
        self.visible_check = QCheckBox()
        self.visible_check.setToolTip("显示/隐藏该文件")
        self.visible_check.setChecked(data_file.config.visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(self.color)
        layout.addWidget(self.label)
        layout.addWidget(self.visible_check)
        self.color.color_changed.connect(lambda color: self.color_changed.emit(self.data_file.file_id, color))
        self.visible_check.toggled.connect(lambda checked: self.toggled.emit(self.data_file.file_id, checked))
        self.update_label()

    def update_label(self) -> None:
        self.label.setText(self.data_file.alias)

    def mouseDoubleClickEvent(self, event):
        alias, ok = QInputDialog.getText(self, "重命名数据文件", "别名：", text=self.data_file.alias)
        if ok and alias.strip():
            self.alias_changed.emit(self.data_file.file_id, alias.strip())
        super().mouseDoubleClickEvent(event)


class LegendBar(QScrollArea):
    toggled = Signal(str, bool)
    alias_changed = Signal(str, str)
    color_changed = Signal(str, str)

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.container = QWidget()
        self.layout = QHBoxLayout(self.container)
        self.layout.setContentsMargins(6, 2, 6, 2)
        self.layout.addStretch(1)
        self.setWidgetResizable(True)
        self.setFixedHeight(54)
        self.setWidget(self.container)

    def refresh(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for data_file in self.data_manager.list_files():
            item = LegendItemWidget(data_file)
            item.toggled.connect(self.toggled.emit)
            item.alias_changed.connect(self.alias_changed.emit)
            item.color_changed.connect(self.color_changed.emit)
            self.layout.addWidget(item)
        self.layout.addStretch(1)
