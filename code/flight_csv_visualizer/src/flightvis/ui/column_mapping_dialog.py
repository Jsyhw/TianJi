from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QVBoxLayout

from flightvis.constants import STANDARD_MAPPING_KEYS


class ColumnMappingDialog(QDialog):
    def __init__(self, columns: list[str], mapping: dict[str, str | None], title: str = "列映射", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.combos: dict[str, QComboBox] = {}
        form = QFormLayout()
        options = [""] + columns
        for key in STANDARD_MAPPING_KEYS:
            combo = QComboBox()
            combo.addItems(options)
            value = mapping.get(key) or ""
            if value in options:
                combo.setCurrentText(value)
            self.combos[key] = combo
            form.addRow(key, combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def mapping(self) -> dict[str, str | None]:
        return {key: combo.currentText() or None for key, combo in self.combos.items()}
