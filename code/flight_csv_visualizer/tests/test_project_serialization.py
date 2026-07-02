from flightvis.models.project_config import ProjectConfig, create_default_project


def test_default_project_round_trips():
    project = create_default_project()
    data = project.to_dict()
    restored = ProjectConfig.from_dict(data)
    assert restored.project_version == project.project_version
    assert len(restored.tabs) == 1
    assert restored.tabs[0].rows == 3
    assert restored.tabs[0].cols == 3
    assert restored.tabs[0].plots[0].preset_variable == "vx"
