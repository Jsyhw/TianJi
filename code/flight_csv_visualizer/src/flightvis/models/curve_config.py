from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CurveConfig:
    curve_id: str
    source: str
    file_id: str
    x_column: str
    y_column: str
    label: str
    use_file_color: bool = True
    color: str | None = None
    line_width: float = 1.5
    line_style: str = "-"
    alpha: float = 1.0
    visible: bool = True
    visibility_version: int = 0

    def to_dict(self) -> dict:
        return {
            "curve_id": self.curve_id,
            "source": self.source,
            "file_id": self.file_id,
            "x_column": self.x_column,
            "y_column": self.y_column,
            "label": self.label,
            "use_file_color": self.use_file_color,
            "color": self.color,
            "line_width": self.line_width,
            "line_style": self.line_style,
            "alpha": self.alpha,
            "visible": self.visible,
            "visibility_version": self.visibility_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CurveConfig":
        return cls(
            curve_id=str(data["curve_id"]),
            source=str(data.get("source", "manual")),
            file_id=str(data["file_id"]),
            x_column=str(data["x_column"]),
            y_column=str(data["y_column"]),
            label=str(data.get("label", "")),
            use_file_color=bool(data.get("use_file_color", True)),
            color=data.get("color"),
            line_width=float(data.get("line_width", 1.5)),
            line_style=str(data.get("line_style", "-")),
            alpha=float(data.get("alpha", 1.0)),
            visible=bool(data.get("visible", True)),
            visibility_version=int(data.get("visibility_version", data.get("visibility_modified_at", 0) or 0)),
        )
