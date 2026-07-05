from pathlib import Path

from flightvis.constants import DEFAULT_COLORS
from flightvis.core.data_manager import DataManager
from flightvis.models.data_file import DataFileConfig
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


def test_hidden_file_color_is_not_reused_for_new_csv():
    project = create_default_project()
    manager = DataManager(project)
    first = manager.add_csv(EXAMPLE)
    second = manager.add_csv(EXAMPLE)
    manager.set_visible(first.file_id, False)
    third = manager.add_csv(EXAMPLE)

    colors = [item.config.color for item in manager.list_files()]
    assert first.config.color != third.config.color
    assert second.config.color != third.config.color
    assert len(colors) == len(set(colors))


def test_new_csv_uses_first_unused_default_color():
    project = create_default_project()
    manager = DataManager(project)
    first = manager.add_csv(EXAMPLE)
    first.config.color = DEFAULT_COLORS[3]
    second = manager.add_csv(EXAMPLE)

    assert second.config.color == DEFAULT_COLORS[0]


def test_new_csv_gets_unique_fallback_color_when_defaults_are_used(monkeypatch):
    import flightvis.core.data_manager as data_manager_module

    monkeypatch.setattr(data_manager_module, "MAX_CSV_FILES", len(DEFAULT_COLORS) + 1)
    project = create_default_project()
    manager = DataManager(project)
    for index, color in enumerate(DEFAULT_COLORS):
        project.data_files.append(
            DataFileConfig(
                file_id=f"existing_{index}",
                path=str(EXAMPLE),
                alias=f"existing{index}",
                color=color,
            )
        )

    added = manager.add_csv(EXAMPLE)

    assert added.config.color
    assert added.config.color not in DEFAULT_COLORS
    assert added.config.color.lower() not in {config.color.lower() for config in project.data_files[:-1]}
