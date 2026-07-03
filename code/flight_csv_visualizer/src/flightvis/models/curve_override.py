from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CurveOverride:
    visible: bool | None = None
    visibility_version: int = 0
    use_file_color: bool | None = None
    color: str | None = None
    line_width: float | None = None
    line_style: str | None = None
    alpha: float | None = None

    def to_dict(self) -> dict:
        return {
            "visible": self.visible,
            "visibility_version": self.visibility_version,
            "use_file_color": self.use_file_color,
            "color": self.color,
            "line_width": self.line_width,
            "line_style": self.line_style,
            "alpha": self.alpha,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "CurveOverride":
        if not data:
            return cls()
        return cls(
            visible=data.get("visible"),
            visibility_version=int(data.get("visibility_version", 0) or 0),
            use_file_color=data.get("use_file_color"),
            color=data.get("color"),
            line_width=float(data["line_width"]) if data.get("line_width") is not None else None,
            line_style=data.get("line_style"),
            alpha=float(data["alpha"]) if data.get("alpha") is not None else None,
        )
