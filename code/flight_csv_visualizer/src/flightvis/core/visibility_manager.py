from __future__ import annotations

from flightvis.models.curve_config import CurveConfig
from flightvis.models.data_file import DataFileConfig
from flightvis.models.visibility import VisibilityState


def effective_preset_curve_visible(
    file_config: DataFileConfig,
    local_visibility: VisibilityState | None,
) -> bool:
    if local_visibility is None:
        return file_config.visible
    if local_visibility.version > file_config.visibility_version:
        return local_visibility.visible
    return file_config.visible


def effective_custom_curve_visible(file_config: DataFileConfig, curve: CurveConfig) -> bool:
    if curve.visibility_version > file_config.visibility_version:
        return curve.visible
    return file_config.visible


def trajectory_visible(file_config: DataFileConfig) -> bool:
    return file_config.visible and not file_config.missing
