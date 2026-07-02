from __future__ import annotations

from pathlib import Path


def export_figure_png(figure, path: str | Path, dpi: int = 200) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(target, dpi=dpi, bbox_inches="tight")
