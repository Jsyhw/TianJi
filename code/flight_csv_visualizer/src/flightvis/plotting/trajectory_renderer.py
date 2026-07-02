from __future__ import annotations

import numpy as np

from flightvis.constants import TRAJECTORY_MAX_POINTS
from flightvis.core.visibility_manager import trajectory_visible
from flightvis.models.data_file import DataFile
from flightvis.plotting.downsample import downsample_xyz
from flightvis.plotting.style import apply_times_font, responsive_font_sizes


def draw_trajectory(ax, data_files: list[DataFile], config: dict | None = None) -> None:
    config = config or {}
    max_points = int(config.get("max_points", TRAJECTORY_MAX_POINTS))
    labels = config.get("labels", {"x": "X", "y": "Y", "z": "Z"})
    show_endpoints = bool(config.get("show_endpoints", True))
    ax.clear()
    all_points: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for data_file in data_files:
        if data_file.dataframe is None or not trajectory_visible(data_file.config):
            continue
        x_col = data_file.mapped_column("x")
        y_col = data_file.mapped_column("y")
        z_col = data_file.mapped_column("z")
        if not x_col or not y_col or not z_col:
            continue
        x, y, z = downsample_xyz(
            data_file.dataframe[x_col].to_numpy(),
            data_file.dataframe[y_col].to_numpy(),
            data_file.dataframe[z_col].to_numpy(),
            max_points,
        )
        ax.plot(x, y, z, label=data_file.alias, color=data_file.config.color, linewidth=1.4)
        if show_endpoints and len(x) > 0:
            ax.scatter([x[0]], [y[0]], [z[0]], color=data_file.config.color, marker="o", s=18)
            ax.scatter([x[-1]], [y[-1]], [z[-1]], color=data_file.config.color, marker="^", s=22)
        all_points.append((np.asarray(x), np.asarray(y), np.asarray(z)))
    sizes = responsive_font_sizes(ax)
    ax.set_xlabel(labels.get("x", "X"), fontsize=sizes["label"])
    ax.set_ylabel(labels.get("y", "Y"), fontsize=sizes["label"])
    ax.set_zlabel(labels.get("z", "Z"), fontsize=sizes["label"])
    ax.set_title("三维轨迹", fontsize=sizes["title"])
    ax.grid(bool(config.get("show_grid", True)))
    if all_points:
        ax.legend(loc="best", fontsize="small")
        if config.get("equal_axis", False):
            set_axes_equal(ax, all_points)
        else:
            set_axes_bounds(ax, all_points)
    apply_times_font(ax)


def set_axes_equal(ax, points: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
    xs = np.concatenate([item[0] for item in points])
    ys = np.concatenate([item[1] for item in points])
    zs = np.concatenate([item[2] for item in points])
    ranges = np.array([xs.max() - xs.min(), ys.max() - ys.min(), zs.max() - zs.min()])
    radius = ranges.max() / 2.0
    centers = np.array([(xs.max() + xs.min()) / 2.0, (ys.max() + ys.min()) / 2.0, (zs.max() + zs.min()) / 2.0])
    if radius == 0:
        radius = 1.0
    ax.set_xlim(centers[0] - radius, centers[0] + radius)
    ax.set_ylim(centers[1] - radius, centers[1] + radius)
    ax.set_zlim(centers[2] - radius, centers[2] + radius)


def set_axes_bounds(ax, points: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
    xs = np.concatenate([item[0] for item in points])
    ys = np.concatenate([item[1] for item in points])
    zs = np.concatenate([item[2] for item in points])
    for values, setter in [
        (xs, ax.set_xlim),
        (ys, ax.set_ylim),
        (zs, ax.set_zlim),
    ]:
        low = float(np.nanmin(values))
        high = float(np.nanmax(values))
        span = high - low
        if not np.isfinite(span) or span == 0:
            span = max(abs(low), 1.0) * 0.02
        pad = span * 0.03
        setter(low - pad, high + pad)
