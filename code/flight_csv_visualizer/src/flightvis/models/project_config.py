from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from flightvis.constants import PROJECT_VERSION, TRAJECTORY_MAX_POINTS
from flightvis.models.data_file import DataFileConfig
from flightvis.models.tab_config import TabConfig, create_default_tab


@dataclass
class ProjectConfig:
    project_version: str = PROJECT_VERSION
    project_name: str = "untitled"
    project_path: str | None = None
    last_modified: str | None = None
    autosave_enabled: bool = True
    visibility_counter: int = 0
    next_file_alias_index: int = 1
    next_file_id_index: int = 1
    next_tab_id_index: int = 1
    next_curve_id_index: int = 1
    window: dict = field(default_factory=dict)
    data_files: list[DataFileConfig] = field(default_factory=list)
    trajectory_view: dict = field(default_factory=lambda: {
        "enabled": True,
        "labels": {"x": "X", "y": "Y", "z": "Z"},
        "show_grid": True,
        "show_endpoints": True,
        "max_points": TRAJECTORY_MAX_POINTS,
        "equal_axis": False,
        "scale_mode": "auto_balanced",
        "z_scale_ratio": 1.0,
        "auto_fit_view": True,
    })
    tabs: list[TabConfig] = field(default_factory=list)
    settings: dict = field(default_factory=dict)

    def touch(self) -> None:
        self.last_modified = datetime.now().isoformat(timespec="seconds")

    def next_visibility_version(self) -> int:
        self.visibility_counter += 1
        return self.visibility_counter

    def allocate_file_id(self) -> str:
        file_id = f"file_{self.next_file_id_index:03d}"
        self.next_file_id_index += 1
        return file_id

    def allocate_alias(self) -> str:
        alias = f"data{self.next_file_alias_index}"
        self.next_file_alias_index += 1
        return alias

    def allocate_tab_id(self) -> str:
        tab_id = f"custom_{self.next_tab_id_index:03d}"
        self.next_tab_id_index += 1
        return tab_id

    def allocate_curve_id(self) -> str:
        curve_id = f"curve_{self.next_curve_id_index:03d}"
        self.next_curve_id_index += 1
        return curve_id

    def to_dict(self) -> dict:
        self.touch()
        return {
            "project_version": self.project_version,
            "project_name": self.project_name,
            "project_path": self.project_path,
            "last_modified": self.last_modified,
            "autosave_enabled": self.autosave_enabled,
            "visibility_counter": self.visibility_counter,
            "next_file_alias_index": self.next_file_alias_index,
            "next_file_id_index": self.next_file_id_index,
            "next_tab_id_index": self.next_tab_id_index,
            "next_curve_id_index": self.next_curve_id_index,
            "window": self.window,
            "data_files": [item.to_dict() for item in self.data_files],
            "trajectory_view": self.trajectory_view,
            "tabs": [tab.to_dict() for tab in self.tabs],
            "settings": self.settings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectConfig":
        project = cls(
            project_version=str(data.get("project_version", PROJECT_VERSION)),
            project_name=str(data.get("project_name", "untitled")),
            project_path=data.get("project_path"),
            last_modified=data.get("last_modified"),
            autosave_enabled=bool(data.get("autosave_enabled", True)),
            visibility_counter=int(data.get("visibility_counter", 0)),
            next_file_alias_index=int(data.get("next_file_alias_index", 1)),
            next_file_id_index=int(data.get("next_file_id_index", 1)),
            next_tab_id_index=int(data.get("next_tab_id_index", 1)),
            next_curve_id_index=int(data.get("next_curve_id_index", 1)),
            window=dict(data.get("window", {})),
            data_files=[DataFileConfig.from_dict(item) for item in data.get("data_files", [])],
            trajectory_view=dict(data.get("trajectory_view", {})),
            tabs=[TabConfig.from_dict(item) for item in data.get("tabs", [])],
            settings=dict(data.get("settings", {})),
        )
        if not project.tabs:
            project.tabs.append(create_default_tab())
        if "scale_mode" not in project.trajectory_view:
            project.trajectory_view["scale_mode"] = "true_equal" if project.trajectory_view.get("equal_axis", False) else "auto_balanced"
        project.trajectory_view.setdefault("z_scale_ratio", 1.0)
        project.trajectory_view.setdefault("auto_fit_view", True)
        return project


def create_default_project() -> ProjectConfig:
    project = ProjectConfig()
    project.tabs.append(create_default_tab())
    return project
