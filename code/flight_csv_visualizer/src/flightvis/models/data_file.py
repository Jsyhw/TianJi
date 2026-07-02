from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class DataFileConfig:
    file_id: str
    path: str
    alias: str
    color: str
    visible: bool = True
    visibility_version: int = 0
    column_mapping: dict[str, str | None] = field(default_factory=dict)
    missing: bool = False

    def to_dict(self) -> dict:
        return {
            "file_id": self.file_id,
            "path": self.path,
            "alias": self.alias,
            "color": self.color,
            "visible": self.visible,
            "visibility_version": self.visibility_version,
            "column_mapping": dict(self.column_mapping),
            "missing": self.missing,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DataFileConfig":
        return cls(
            file_id=str(data["file_id"]),
            path=str(data["path"]),
            alias=str(data["alias"]),
            color=str(data.get("color", "#1f77b4")),
            visible=bool(data.get("visible", True)),
            visibility_version=int(data.get("visibility_version", data.get("visibility_modified_at", 0) or 0)),
            column_mapping=dict(data.get("column_mapping", {})),
            missing=bool(data.get("missing", False)),
        )


@dataclass
class DataFile:
    config: DataFileConfig
    dataframe: "pd.DataFrame | None"
    columns: list[str] = field(default_factory=list)
    row_count: int = 0

    @property
    def file_id(self) -> str:
        return self.config.file_id

    @property
    def alias(self) -> str:
        return self.config.alias

    def mapped_column(self, key: str) -> str | None:
        column = self.config.column_mapping.get(key)
        if column and column in self.columns:
            return column
        return None

    def has_columns(self, *keys: str) -> bool:
        return all(self.mapped_column(key) for key in keys)
