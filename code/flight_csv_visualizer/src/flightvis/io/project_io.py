from __future__ import annotations

import json
import os
from pathlib import Path

from flightvis.models.project_config import ProjectConfig


def save_project(project: ProjectConfig, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(project.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, target)
    project.project_path = str(target)


def load_project(path: str | Path) -> ProjectConfig:
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    project = ProjectConfig.from_dict(data)
    project.project_path = str(source)
    return project
