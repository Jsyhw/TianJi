from flightvis.models.project_config import ProjectConfig, create_default_project
from flightvis.models.curve_override import CurveOverride
from flightvis.models.tab_config import create_custom_tab


def test_default_project_round_trips():
    project = create_default_project()
    project.settings["last_csv_dir"] = "D:/data"
    plot = project.tabs[0].plots[0]
    plot.curve_order = ["file_002", "file_001"]
    plot.curve_overrides["file_001"] = CurveOverride(
        visible=False,
        visibility_version=7,
        use_file_color=False,
        color="#123456",
        line_width=2.5,
        line_style="--",
        alpha=0.55,
    )
    data = project.to_dict()
    restored = ProjectConfig.from_dict(data)
    assert restored.project_version == project.project_version
    assert len(restored.tabs) == 1
    assert restored.tabs[0].rows == 3
    assert restored.tabs[0].cols == 3
    assert restored.tabs[0].plots[0].preset_variable == "vx"
    assert restored.settings["last_csv_dir"] == "D:/data"
    restored_plot = restored.tabs[0].plots[0]
    assert restored_plot.curve_order == ["file_002", "file_001"]
    assert restored_plot.curve_overrides["file_001"].color == "#123456"
    assert restored_plot.curve_overrides["file_001"].alpha == 0.55


def test_horizontal_compare_column_mapping_round_trips():
    project = create_default_project()
    project.tabs.append(create_custom_tab("custom_001", "custom", 1, 1))
    custom_plot = project.tabs[1].plots[0]
    custom_plot.horizontal_compare.y_column_by_file = {"file_001": "vx"}
    restored = ProjectConfig.from_dict(project.to_dict())
    assert restored.tabs[1].plots[0].horizontal_compare.y_column_by_file == {"file_001": "vx"}
