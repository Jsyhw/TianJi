from __future__ import annotations

import matplotlib

from flightvis.constants import DEFAULT_COLORS

PLOT_FONT_FAMILY = ["Times New Roman", "Microsoft YaHei", "SimSun", "DejaVu Sans"]


def configure_matplotlib_fonts() -> None:
    matplotlib.rcParams["font.family"] = PLOT_FONT_FAMILY
    matplotlib.rcParams["axes.unicode_minus"] = False


def variable_color(index: int) -> str:
    return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]


def apply_times_font(ax) -> None:
    sizes = responsive_font_sizes(ax)
    title = ax.title
    _apply_label_font(title)
    title.set_fontsize(sizes["title"])
    _apply_label_font(ax.xaxis.label)
    ax.xaxis.label.set_fontsize(sizes["label"])
    _apply_label_font(ax.yaxis.label)
    ax.yaxis.label.set_fontsize(sizes["label"])
    if hasattr(ax, "zaxis"):
        _apply_label_font(ax.zaxis.label)
        ax.zaxis.label.set_fontsize(sizes["label"])
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname("Times New Roman")
        label.set_fontsize(sizes["tick"])
    if hasattr(ax, "get_zticklabels"):
        for label in ax.get_zticklabels():
            label.set_fontname("Times New Roman")
            label.set_fontsize(sizes["tick"])
    legend = ax.get_legend()
    if legend:
        for text in legend.get_texts():
            _apply_label_font(text)
            text.set_fontsize(sizes["legend"])


def _apply_label_font(text) -> None:
    value = text.get_text()
    if value and any(ord(char) > 127 for char in value):
        text.set_fontfamily(PLOT_FONT_FAMILY)
    else:
        text.set_fontname("Times New Roman")


def responsive_font_sizes(ax) -> dict[str, float]:
    try:
        width, height = ax.figure.canvas.get_width_height()
    except Exception:
        width, height = ax.figure.bbox.width, ax.figure.bbox.height
    base = max(6.0, min(13.0, min(width, height) / 28.0))
    return {
        "title": base,
        "label": max(5.5, base * 0.78),
        "tick": max(5.0, base * 0.68),
        "legend": max(5.0, base * 0.66),
    }
