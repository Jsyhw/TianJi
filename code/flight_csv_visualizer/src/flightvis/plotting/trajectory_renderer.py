from __future__ import annotations

import numpy as np

from flightvis.constants import TRAJECTORY_MAX_POINTS
from flightvis.core.visibility_manager import effective_custom_curve_visible
from flightvis.models.curve_config import CurveConfig
from flightvis.models.curve_override import CurveOverride
from flightvis.models.data_file import DataFile
from flightvis.plotting.downsample import downsample_xyz
from flightvis.plotting.plot_renderer import apply_curve_override, order_curves
from flightvis.plotting.style import apply_times_font, responsive_font_sizes

TRAJECTORY_SCALE_AUTO = "auto_balanced"
TRAJECTORY_SCALE_TRUE = "true_equal"
TRAJECTORY_SCALE_FREE = "free"
TRAJECTORY_SCALE_CUSTOM_Z = "custom_z"
AUTO_Z_MIN_RATIO = 0.35
AUTO_Z_MAX_RATIO = 2.0
DEFAULT_Z_SCALE_RATIO = 1.0


def build_trajectory_display_curves(data_files: list[DataFile], config: dict | None = None) -> list[CurveConfig]:
    config = config or {}
    curves: list[CurveConfig] = []
    overrides = config.get("curve_overrides", {})
    for data_file in data_files:
        if data_file.dataframe is None or data_file.config.missing:
            continue
        x_col = data_file.mapped_column("x")
        y_col = data_file.mapped_column("y")
        z_col = data_file.mapped_column("z")
        if not x_col or not y_col or not z_col:
            continue
        curve = CurveConfig(
            curve_id=data_file.file_id,
            source="trajectory",
            file_id=data_file.file_id,
            x_column=x_col,
            y_column=y_col,
            label=data_file.alias,
            use_file_color=True,
            color=data_file.config.color,
            line_width=1.4,
            line_style="-",
            alpha=1.0,
            visible=data_file.config.visible,
        )
        curves.append(apply_curve_override(curve, curve_override_from_config(overrides.get(curve.curve_id))))
    return order_curves(curves, [str(item) for item in config.get("curve_order", [])])


def curve_override_from_config(value) -> CurveOverride | None:
    if isinstance(value, CurveOverride):
        return value
    if isinstance(value, dict):
        return CurveOverride.from_dict(value)
    return None


def draw_trajectory(ax, data_files: list[DataFile], config: dict | None = None) -> None:
    config = config or {}
    max_points = int(config.get("max_points", TRAJECTORY_MAX_POINTS))
    labels = config.get("labels", {"x": "X", "y": "Y", "z": "Z"})
    show_endpoints = bool(config.get("show_endpoints", True))
    ax.clear()
    all_points: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    curves = build_trajectory_display_curves(data_files, config)
    for curve in reversed(curves):
        data_file = next((item for item in data_files if item.file_id == curve.file_id), None)
        if data_file is None or data_file.dataframe is None or not effective_custom_curve_visible(data_file.config, curve):
            continue
        z_col = data_file.mapped_column("z")
        if not z_col or curve.x_column not in data_file.columns or curve.y_column not in data_file.columns:
            continue
        x, y, z = downsample_xyz(
            data_file.dataframe[curve.x_column].to_numpy(),
            data_file.dataframe[curve.y_column].to_numpy(),
            data_file.dataframe[z_col].to_numpy(),
            max_points,
        )
        color = data_file.config.color if curve.use_file_color else curve.color
        ax.plot(
            x,
            y,
            z,
            label=curve.label,
            color=color or data_file.config.color,
            linewidth=curve.line_width,
            linestyle=curve.line_style,
            alpha=curve.alpha,
        )
        if show_endpoints and len(x) > 0:
            ax.scatter([x[0]], [y[0]], [z[0]], color=color or data_file.config.color, marker="o", s=18, alpha=curve.alpha)
            ax.scatter([x[-1]], [y[-1]], [z[-1]], color=color or data_file.config.color, marker="^", s=22, alpha=curve.alpha)
        all_points.append((np.asarray(x), np.asarray(y), np.asarray(z)))
    sizes = responsive_font_sizes(ax)
    ax.set_xlabel(labels.get("x", "X"), fontsize=sizes["label"])
    ax.set_ylabel(labels.get("y", "Y"), fontsize=sizes["label"])
    ax.set_zlabel(labels.get("z", "Z"), fontsize=sizes["label"])
    ax.set_title("三维轨迹", fontsize=sizes["title"])
    ax.grid(bool(config.get("show_grid", True)))
    if all_points:
        ax.legend(loc="best", fontsize="small")
        apply_scale_mode(ax, all_points, config)
    apply_times_font(ax)


def resolve_scale_mode(config: dict | None) -> str:
    config = config or {}
    mode = config.get("scale_mode")
    if mode in {
        TRAJECTORY_SCALE_AUTO,
        TRAJECTORY_SCALE_TRUE,
        TRAJECTORY_SCALE_FREE,
        TRAJECTORY_SCALE_CUSTOM_Z,
    }:
        return str(mode)
    return TRAJECTORY_SCALE_TRUE if config.get("equal_axis", False) else TRAJECTORY_SCALE_AUTO


def apply_scale_mode(ax, points: list[tuple[np.ndarray, np.ndarray, np.ndarray]], config: dict | None = None) -> None:
    xs = np.concatenate([item[0] for item in points])
    ys = np.concatenate([item[1] for item in points])
    zs = np.concatenate([item[2] for item in points])
    x_span = set_axis_bounds(xs, ax.set_xlim)
    y_span = set_axis_bounds(ys, ax.set_ylim)
    z_span = set_axis_bounds(zs, ax.set_zlim)
    mode = resolve_scale_mode(config)
    if mode == TRAJECTORY_SCALE_FREE or not hasattr(ax, "set_box_aspect"):
        return
    xy_ref = max(x_span, y_span, 1e-9)
    if mode == TRAJECTORY_SCALE_AUTO:
        z_display_span = min(max(z_span, xy_ref * AUTO_Z_MIN_RATIO), xy_ref * AUTO_Z_MAX_RATIO)
    elif mode == TRAJECTORY_SCALE_CUSTOM_Z:
        ratio = float((config or {}).get("z_scale_ratio", DEFAULT_Z_SCALE_RATIO) or DEFAULT_Z_SCALE_RATIO)
        z_display_span = xy_ref * min(max(ratio, 0.2), 5.0)
    else:
        z_display_span = z_span
    ax.set_box_aspect((x_span, y_span, z_display_span))


def set_axes_equal(ax, points: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
    apply_scale_mode(ax, points, {"scale_mode": TRAJECTORY_SCALE_TRUE})


def set_axes_auto_balanced(ax, points: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
    apply_scale_mode(ax, points, {"scale_mode": TRAJECTORY_SCALE_AUTO})


def set_axes_custom_z(ax, points: list[tuple[np.ndarray, np.ndarray, np.ndarray]], z_scale_ratio: float) -> None:
    apply_scale_mode(ax, points, {"scale_mode": TRAJECTORY_SCALE_CUSTOM_Z, "z_scale_ratio": z_scale_ratio})


def set_axes_bounds(ax, points: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
    xs = np.concatenate([item[0] for item in points])
    ys = np.concatenate([item[1] for item in points])
    zs = np.concatenate([item[2] for item in points])
    for values, setter in [
        (xs, ax.set_xlim),
        (ys, ax.set_ylim),
        (zs, ax.set_zlim),
    ]:
        set_axis_bounds(values, setter)


def set_axis_bounds(values: np.ndarray, setter) -> float:
    low = float(np.nanmin(values))
    high = float(np.nanmax(values))
    span = high - low
    if not np.isfinite(span) or span == 0:
        span = max(abs(low), 1.0) * 0.02
    pad = span * 0.03
    setter(low - pad, high + pad)
    return span + 2 * pad
