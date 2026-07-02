from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    data_files_changed = Signal()
    file_visibility_changed = Signal(str)
    file_color_changed = Signal(str)
    file_alias_changed = Signal(str)
    plot_config_changed = Signal(str)
    curve_visibility_changed = Signal(str)
    project_loaded = Signal()
