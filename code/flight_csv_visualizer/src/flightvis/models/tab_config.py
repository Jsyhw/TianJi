from __future__ import annotations

from dataclasses import dataclass, field

from flightvis.constants import PRESET_PLOTS
from flightvis.models.plot_config import (
    CustomPlotConfig,
    DisplayConfig,
    PresetPlotConfig,
    plot_from_dict,
)


@dataclass
class TabConfig:
    tab_id: str
    name: str
    tab_type: str
    rows: int
    cols: int
    plots: list[PresetPlotConfig | CustomPlotConfig] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tab_id": self.tab_id,
            "name": self.name,
            "tab_type": self.tab_type,
            "rows": self.rows,
            "cols": self.cols,
            "plots": [plot.to_dict() for plot in self.plots],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TabConfig":
        return cls(
            tab_id=str(data["tab_id"]),
            name=str(data.get("name", "Untitled")),
            tab_type=str(data.get("tab_type", "custom")),
            rows=int(data.get("rows", 1)),
            cols=int(data.get("cols", 1)),
            plots=[plot_from_dict(item) for item in data.get("plots", [])],
        )


def create_default_tab() -> TabConfig:
    plots: list[PresetPlotConfig] = []
    for index, (variable, title, y_label) in enumerate(PRESET_PLOTS):
        row = index // 3
        col = index % 3
        plots.append(
            PresetPlotConfig(
                plot_id=f"preset_{variable}",
                preset_variable=variable,
                row=row,
                col=col,
                title=title,
                display=DisplayConfig(x_label="time", y_label=y_label, show_grid=True),
            )
        )
    return TabConfig(tab_id="default", name="基本状态量", tab_type="default", rows=3, cols=3, plots=plots)


def create_custom_tab(tab_id: str, name: str, rows: int, cols: int) -> TabConfig:
    plots: list[CustomPlotConfig] = []
    for row in range(rows):
        for col in range(cols):
            plots.append(CustomPlotConfig(plot_id=f"{tab_id}_plot_{row}_{col}", row=row, col=col))
    return TabConfig(tab_id=tab_id, name=name, tab_type="custom", rows=rows, cols=cols, plots=plots)
