from __future__ import annotations

from flightvis.core.visibility_manager import effective_custom_curve_visible
from flightvis.models.curve_config import CurveConfig
from flightvis.models.curve_override import CurveOverride
from flightvis.models.data_file import DataFile
from flightvis.models.plot_config import CustomPlotConfig, PresetPlotConfig
from flightvis.plotting.style import apply_times_font, responsive_font_sizes, variable_color


def apply_curve_override(curve: CurveConfig, override: CurveOverride | None) -> CurveConfig:
    if not override:
        return curve
    if override.visible is not None:
        curve.visible = override.visible
        curve.visibility_version = override.visibility_version
    if override.use_file_color is not None:
        curve.use_file_color = override.use_file_color
    if override.color:
        curve.color = override.color
    if override.line_width is not None:
        curve.line_width = override.line_width
    if override.line_style:
        curve.line_style = override.line_style
    if override.alpha is not None:
        curve.alpha = override.alpha
    return curve


def order_curves(curves: list[CurveConfig], curve_order: list[str]) -> list[CurveConfig]:
    by_id = {curve.curve_id: curve for curve in curves}
    ordered = [by_id[curve_id] for curve_id in curve_order if curve_id in by_id]
    ordered_ids = {curve.curve_id for curve in ordered}
    ordered.extend(curve for curve in curves if curve.curve_id not in ordered_ids)
    return ordered


def build_preset_display_curves(plot: PresetPlotConfig, data_files: list[DataFile]) -> list[CurveConfig]:
    curves: list[CurveConfig] = []
    for data_file in data_files:
        if data_file.dataframe is None or data_file.config.missing:
            continue
        x_col = data_file.mapped_column("time")
        y_col = data_file.mapped_column(plot.preset_variable)
        if not x_col or not y_col:
            continue
        local = plot.curve_visibility.get(data_file.file_id)
        curve = CurveConfig(
            curve_id=data_file.file_id,
            source="preset",
            file_id=data_file.file_id,
            x_column=x_col,
            y_column=y_col,
            label=data_file.alias,
            use_file_color=True,
            color=data_file.config.color,
            line_width=plot.display.line_width,
            line_style=plot.display.line_style,
            visible=local.visible if local else data_file.config.visible,
            visibility_version=local.version if local else 0,
        )
        curves.append(apply_curve_override(curve, plot.curve_overrides.get(curve.curve_id)))
    return order_curves(curves, plot.curve_order)


def draw_preset_plot(ax, plot: PresetPlotConfig, data_files: list[DataFile]) -> None:
    ax.clear()
    drawn = False
    for curve in reversed(build_preset_display_curves(plot, data_files)):
        data_file = next((item for item in data_files if item.file_id == curve.file_id), None)
        if not data_file or data_file.dataframe is None or data_file.config.missing:
            continue
        if not effective_custom_curve_visible(data_file.config, curve):
            continue
        color = data_file.config.color if curve.use_file_color else curve.color
        ax.plot(
            data_file.dataframe[curve.x_column],
            data_file.dataframe[curve.y_column],
            label=curve.label,
            color=color or data_file.config.color,
            linewidth=curve.line_width,
            linestyle=curve.line_style,
            alpha=curve.alpha,
        )
        drawn = True
    apply_display(ax, plot.title, plot.display)
    if plot.display.show_local_legend and drawn:
        ax.legend(loc="best", fontsize="small")
    apply_times_font(ax)


def build_horizontal_curves(plot: CustomPlotConfig, data_files: list[DataFile]) -> list[CurveConfig]:
    config = plot.horizontal_compare
    if not config.enabled or not config.y_variable:
        return []
    included = None if config.included_file_ids == "all" else set(config.included_file_ids)
    curves: list[CurveConfig] = []
    for data_file in data_files:
        if data_file.dataframe is None or data_file.config.missing:
            continue
        if included is not None and data_file.file_id not in included:
            continue
        x_col = data_file.mapped_column("time") if config.x_mode == "mapped_time" else config.x_column
        y_col = config.y_column_by_file.get(data_file.file_id)
        if not y_col:
            mapped_col = data_file.mapped_column(config.y_variable)
            y_col = mapped_col if mapped_col in data_file.columns else config.y_variable
        if not x_col or not y_col or x_col not in data_file.columns or y_col not in data_file.columns:
            continue
        curve_id = f"{plot.plot_id}_{data_file.file_id}_{x_col}_{y_col}_horizontal"
        generated_visible = plot.generated_curve_visibility.get(curve_id, True)
        curves.append(
            apply_curve_override(CurveConfig(
                curve_id=curve_id,
                source="horizontal_compare",
                file_id=data_file.file_id,
                x_column=x_col,
                y_column=y_col,
                label=f"{data_file.alias} / {y_col}",
                line_width=plot.display.line_width,
                line_style=plot.display.line_style,
                alpha=1.0,
                visible=generated_visible,
                visibility_version=1 if curve_id in plot.generated_curve_visibility else 0,
            ), plot.curve_overrides.get(curve_id))
        )
    return curves


def build_vertical_curves(plot: CustomPlotConfig, data_files: list[DataFile]) -> list[CurveConfig]:
    config = plot.vertical_compare
    if not config.enabled or not config.file_id or not config.y_columns:
        return []
    data_file = next((item for item in data_files if item.file_id == config.file_id), None)
    if not data_file or data_file.dataframe is None or data_file.config.missing:
        return []
    if config.x_column not in data_file.columns:
        return []
    curves: list[CurveConfig] = []
    for index, y_col in enumerate(config.y_columns):
        if y_col not in data_file.columns:
            continue
        curve_id = f"{plot.plot_id}_{data_file.file_id}_{config.x_column}_{y_col}_vertical"
        generated_visible = plot.generated_curve_visibility.get(curve_id, True)
        curves.append(
            apply_curve_override(CurveConfig(
                curve_id=curve_id,
                source="vertical_compare",
                file_id=data_file.file_id,
                x_column=config.x_column,
                y_column=y_col,
                label=f"{data_file.alias} / {y_col}",
                use_file_color=False,
                color=variable_color(index),
                line_width=plot.display.line_width,
                line_style=plot.display.line_style,
                alpha=1.0,
                visible=generated_visible,
                visibility_version=1 if curve_id in plot.generated_curve_visibility else 0,
            ), plot.curve_overrides.get(curve_id))
        )
    return curves


def build_custom_display_curves(plot: CustomPlotConfig, data_files: list[DataFile]) -> list[CurveConfig]:
    generated: list[CurveConfig] = []
    generated.extend(build_horizontal_curves(plot, data_files))
    generated.extend(build_vertical_curves(plot, data_files))
    manual = [
        apply_curve_override(curve, plot.curve_overrides.get(curve.curve_id))
        for curve in list(plot.curves)
    ]
    return order_curves(generated + manual, plot.curve_order)


def draw_custom_plot(ax, plot: CustomPlotConfig, data_files: list[DataFile]) -> None:
    ax.clear()
    curves = build_custom_display_curves(plot, data_files)
    drawn = False
    for curve in reversed(curves):
        data_file = next((item for item in data_files if item.file_id == curve.file_id), None)
        if not data_file or data_file.dataframe is None or data_file.config.missing:
            continue
        if curve.x_column not in data_file.columns or curve.y_column not in data_file.columns:
            continue
        if not effective_custom_curve_visible(data_file.config, curve):
            continue
        color = data_file.config.color if curve.use_file_color else curve.color
        ax.plot(
            data_file.dataframe[curve.x_column],
            data_file.dataframe[curve.y_column],
            label=curve.label,
            color=color or data_file.config.color,
            linewidth=curve.line_width,
            linestyle=curve.line_style,
            alpha=curve.alpha,
        )
        drawn = True
    apply_display(ax, plot.title, plot.display)
    if plot.display.show_local_legend and drawn:
        ax.legend(loc="best", fontsize="small")
    apply_times_font(ax)


def apply_display(ax, title: str, display) -> None:
    sizes = responsive_font_sizes(ax)
    ax.set_title(title, fontsize=sizes["title"])
    ax.set_xlabel(display.x_label, fontsize=sizes["label"])
    ax.set_ylabel(display.y_label, fontsize=sizes["label"])
    ax.grid(display.show_grid)
    if display.x_range:
        ax.set_xlim(*display.x_range)
    if display.y_range:
        ax.set_ylim(*display.y_range)
    apply_times_font(ax)
