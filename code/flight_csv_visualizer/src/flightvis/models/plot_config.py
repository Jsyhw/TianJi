from __future__ import annotations

from dataclasses import dataclass, field

from flightvis.models.curve_config import CurveConfig
from flightvis.models.curve_override import CurveOverride
from flightvis.models.serialization import optional_float_range
from flightvis.models.visibility import VisibilityState


@dataclass
class DisplayConfig:
    x_label: str = "time"
    y_label: str = "value"
    show_grid: bool = True
    show_local_legend: bool = False
    x_range: tuple[float, float] | None = None
    y_range: tuple[float, float] | None = None
    line_width: float = 1.5
    line_style: str = "-"

    def to_dict(self) -> dict:
        return {
            "x_label": self.x_label,
            "y_label": self.y_label,
            "show_grid": self.show_grid,
            "show_local_legend": self.show_local_legend,
            "x_range": list(self.x_range) if self.x_range else None,
            "y_range": list(self.y_range) if self.y_range else None,
            "line_width": self.line_width,
            "line_style": self.line_style,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "DisplayConfig":
        if not data:
            return cls()
        return cls(
            x_label=str(data.get("x_label", "time")),
            y_label=str(data.get("y_label", "value")),
            show_grid=bool(data.get("show_grid", True)),
            show_local_legend=bool(data.get("show_local_legend", False)),
            x_range=optional_float_range(data.get("x_range")),
            y_range=optional_float_range(data.get("y_range")),
            line_width=float(data.get("line_width", 1.5)),
            line_style=str(data.get("line_style", "-")),
        )


@dataclass
class PresetPlotConfig:
    plot_id: str
    plot_type: str = "preset"
    preset_variable: str = "vx"
    row: int = 0
    col: int = 0
    row_span: int = 1
    col_span: int = 1
    title: str = ""
    display: DisplayConfig = field(default_factory=DisplayConfig)
    curve_visibility: dict[str, VisibilityState] = field(default_factory=dict)
    curve_overrides: dict[str, CurveOverride] = field(default_factory=dict)
    curve_order: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "plot_id": self.plot_id,
            "plot_type": self.plot_type,
            "preset_variable": self.preset_variable,
            "row": self.row,
            "col": self.col,
            "row_span": self.row_span,
            "col_span": self.col_span,
            "title": self.title,
            "display": self.display.to_dict(),
            "curve_visibility": {key: value.to_dict() for key, value in self.curve_visibility.items()},
            "curve_overrides": {key: value.to_dict() for key, value in self.curve_overrides.items()},
            "curve_order": list(self.curve_order),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PresetPlotConfig":
        return cls(
            plot_id=str(data["plot_id"]),
            plot_type="preset",
            preset_variable=str(data.get("preset_variable", "vx")),
            row=int(data.get("row", 0)),
            col=int(data.get("col", 0)),
            row_span=max(1, int(data.get("row_span", 1))),
            col_span=max(1, int(data.get("col_span", 1))),
            title=str(data.get("title", "")),
            display=DisplayConfig.from_dict(data.get("display")),
            curve_visibility={
                str(key): VisibilityState.from_dict(value)
                for key, value in data.get("curve_visibility", {}).items()
            },
            curve_overrides={
                str(key): CurveOverride.from_dict(value)
                for key, value in data.get("curve_overrides", {}).items()
            },
            curve_order=[str(item) for item in data.get("curve_order", [])],
        )


@dataclass
class HorizontalCompareConfig:
    enabled: bool = False
    compare_by: str = "mapped_variable"
    x_mode: str = "mapped_time"
    x_column: str = "time"
    y_variable: str | None = None
    y_column_by_file: dict[str, str] = field(default_factory=dict)
    included_file_ids: list[str] | str = "all"
    auto_include_new_files: bool = True
    missing_column_policy: str = "skip_with_warning"

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "compare_by": self.compare_by,
            "x_mode": self.x_mode,
            "x_column": self.x_column,
            "y_variable": self.y_variable,
            "y_column_by_file": dict(self.y_column_by_file),
            "included_file_ids": self.included_file_ids,
            "auto_include_new_files": self.auto_include_new_files,
            "missing_column_policy": self.missing_column_policy,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "HorizontalCompareConfig":
        if not data:
            return cls()
        included = data.get("included_file_ids", "all")
        if included != "all":
            included = list(included)
        return cls(
            enabled=bool(data.get("enabled", False)),
            compare_by=str(data.get("compare_by", "mapped_variable")),
            x_mode=str(data.get("x_mode", "mapped_time")),
            x_column=str(data.get("x_column", "time")),
            y_variable=data.get("y_variable"),
            y_column_by_file={str(key): str(value) for key, value in data.get("y_column_by_file", {}).items()},
            included_file_ids=included,
            auto_include_new_files=bool(data.get("auto_include_new_files", True)),
            missing_column_policy=str(data.get("missing_column_policy", "skip_with_warning")),
        )


@dataclass
class VerticalCompareConfig:
    enabled: bool = False
    file_id: str | None = None
    x_column: str = "time"
    y_columns: list[str] = field(default_factory=list)
    color_strategy: str = "auto_by_variable"
    show_local_legend: bool = True
    on_file_changed: str = "reuse_columns_if_available"
    missing_column_policy: str = "keep_available_and_warn"

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "file_id": self.file_id,
            "x_column": self.x_column,
            "y_columns": list(self.y_columns),
            "color_strategy": self.color_strategy,
            "show_local_legend": self.show_local_legend,
            "on_file_changed": self.on_file_changed,
            "missing_column_policy": self.missing_column_policy,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "VerticalCompareConfig":
        if not data:
            return cls()
        return cls(
            enabled=bool(data.get("enabled", False)),
            file_id=data.get("file_id"),
            x_column=str(data.get("x_column", "time")),
            y_columns=list(data.get("y_columns", [])),
            color_strategy=str(data.get("color_strategy", "auto_by_variable")),
            show_local_legend=bool(data.get("show_local_legend", True)),
            on_file_changed=str(data.get("on_file_changed", "reuse_columns_if_available")),
            missing_column_policy=str(data.get("missing_column_policy", "keep_available_and_warn")),
        )


@dataclass
class CustomPlotConfig:
    plot_id: str
    plot_type: str = "custom"
    plot_mode: str = "manual"
    row: int = 0
    col: int = 0
    row_span: int = 1
    col_span: int = 1
    title: str = "未配置图窗"
    display: DisplayConfig = field(default_factory=DisplayConfig)
    horizontal_compare: HorizontalCompareConfig = field(default_factory=HorizontalCompareConfig)
    vertical_compare: VerticalCompareConfig = field(default_factory=VerticalCompareConfig)
    curves: list[CurveConfig] = field(default_factory=list)
    generated_curve_visibility: dict[str, bool] = field(default_factory=dict)
    curve_overrides: dict[str, CurveOverride] = field(default_factory=dict)
    curve_order: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "plot_id": self.plot_id,
            "plot_type": self.plot_type,
            "plot_mode": self.plot_mode,
            "row": self.row,
            "col": self.col,
            "row_span": self.row_span,
            "col_span": self.col_span,
            "title": self.title,
            "display": self.display.to_dict(),
            "horizontal_compare": self.horizontal_compare.to_dict(),
            "vertical_compare": self.vertical_compare.to_dict(),
            "curves": [curve.to_dict() for curve in self.curves],
            "generated_curve_visibility": dict(self.generated_curve_visibility),
            "curve_overrides": {key: value.to_dict() for key, value in self.curve_overrides.items()},
            "curve_order": list(self.curve_order),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CustomPlotConfig":
        curve_overrides = {
            str(key): CurveOverride.from_dict(value)
            for key, value in data.get("curve_overrides", {}).items()
        }
        for curve_id, visible in data.get("generated_curve_visibility", {}).items():
            curve_overrides.setdefault(str(curve_id), CurveOverride(visible=bool(visible)))
        return cls(
            plot_id=str(data["plot_id"]),
            plot_type="custom",
            plot_mode=str(data.get("plot_mode", "manual")),
            row_span=max(1, int(data.get("row_span", 1))),
            col_span=max(1, int(data.get("col_span", 1))),
            row=int(data.get("row", 0)),
            col=int(data.get("col", 0)),
            title=str(data.get("title", "未配置图窗")),
            display=DisplayConfig.from_dict(data.get("display")),
            horizontal_compare=HorizontalCompareConfig.from_dict(data.get("horizontal_compare")),
            vertical_compare=VerticalCompareConfig.from_dict(data.get("vertical_compare")),
            curves=[CurveConfig.from_dict(item) for item in data.get("curves", [])],
            generated_curve_visibility=dict(data.get("generated_curve_visibility", {})),
            curve_overrides=curve_overrides,
            curve_order=[str(item) for item in data.get("curve_order", [])],
        )


def plot_from_dict(data: dict) -> PresetPlotConfig | CustomPlotConfig:
    if data.get("plot_type") == "custom":
        return CustomPlotConfig.from_dict(data)
    return PresetPlotConfig.from_dict(data)
