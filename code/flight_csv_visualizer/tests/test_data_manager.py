from pathlib import Path

from flightvis.core.data_manager import DataManager
from flightvis.models.project_config import create_default_project


EXAMPLE = Path(__file__).resolve().parents[3] / "example" / "exampe-1.csv"


def test_add_sample_csv_detects_mapping():
    project = create_default_project()
    manager = DataManager(project)
    data_file = manager.add_csv(EXAMPLE)
    assert data_file.alias == "data1"
    assert data_file.row_count > 0
    assert data_file.config.column_mapping["roll"] == "phi"


def test_alias_counter_does_not_reuse_after_delete():
    project = create_default_project()
    manager = DataManager(project)
    first = manager.add_csv(EXAMPLE)
    second = manager.add_csv(EXAMPLE)
    manager.remove_file(second.file_id)
    third = manager.add_csv(EXAMPLE)
    assert first.alias == "data1"
    assert second.alias == "data2"
    assert third.alias == "data3"
