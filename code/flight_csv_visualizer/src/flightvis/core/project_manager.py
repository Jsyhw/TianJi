from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal

from flightvis.io.project_io import load_project, save_project
from flightvis.models.project_config import ProjectConfig, create_default_project
from flightvis.settings import default_autosave_path


class ProjectManager(QObject):
    dirty_changed = Signal(bool)

    def __init__(self, project: ProjectConfig | None = None):
        super().__init__()
        self.project = project or create_default_project()
        self.dirty = False
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(1000)
        self.autosave_timer.timeout.connect(self.autosave)

    def set_project(self, project: ProjectConfig) -> None:
        self.project = project
        self.dirty = False
        self.dirty_changed.emit(False)

    def mark_dirty(self) -> None:
        self.dirty = True
        self.dirty_changed.emit(True)
        if self.project.autosave_enabled:
            self.autosave_timer.start()

    def save(self, path: str | Path | None = None) -> None:
        target = Path(path or self.project.project_path or default_autosave_path())
        save_project(self.project, target)
        self.dirty = False
        self.dirty_changed.emit(False)

    def save_as(self, path: str | Path) -> None:
        self.project.project_path = str(path)
        self.save(path)

    def autosave(self) -> None:
        if not self.dirty or not self.project.autosave_enabled:
            return
        target = self.project.project_path or default_autosave_path()
        self.save(target)

    def load(self, path: str | Path) -> ProjectConfig:
        project = load_project(path)
        self.set_project(project)
        return project
