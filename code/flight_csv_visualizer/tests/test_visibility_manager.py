from flightvis.core.visibility_manager import effective_custom_curve_visible, effective_preset_curve_visible, trajectory_visible
from flightvis.models.curve_config import CurveConfig
from flightvis.models.data_file import DataFileConfig
from flightvis.models.visibility import VisibilityState


def make_file(visible=True, version=0):
    return DataFileConfig("file_001", "a.csv", "data1", "#111111", visible=visible, visibility_version=version)


def test_preset_uses_file_when_no_local_state():
    assert effective_preset_curve_visible(make_file(False, 4), None) is False


def test_preset_local_newer_overrides_global():
    file_config = make_file(False, 4)
    local = VisibilityState(True, 5)
    assert effective_preset_curve_visible(file_config, local) is True


def test_preset_global_newer_overrides_local():
    file_config = make_file(True, 6)
    local = VisibilityState(False, 5)
    assert effective_preset_curve_visible(file_config, local) is True


def test_custom_curve_newer_overrides_global():
    file_config = make_file(False, 2)
    curve = CurveConfig("curve_001", "manual", "file_001", "time", "vx", "data1 / vx", visible=True, visibility_version=3)
    assert effective_custom_curve_visible(file_config, curve) is True


def test_trajectory_only_uses_global_state():
    file_config = make_file(False, 10)
    assert trajectory_visible(file_config) is False
