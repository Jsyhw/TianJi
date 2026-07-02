from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VisibilityState:
    visible: bool = True
    version: int = 0

    def to_dict(self) -> dict:
        return {"visible": self.visible, "version": self.version}

    @classmethod
    def from_dict(cls, data: dict | None) -> "VisibilityState":
        if not data:
            return cls()
        return cls(visible=bool(data.get("visible", True)), version=int(data.get("version", 0)))
