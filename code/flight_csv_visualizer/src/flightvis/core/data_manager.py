from __future__ import annotations

from pathlib import Path

from flightvis.constants import DEFAULT_COLORS, MAX_CSV_FILES
from flightvis.io.column_detector import detect_column_mapping
from flightvis.io.csv_loader import read_csv
from flightvis.models.data_file import DataFile, DataFileConfig
from flightvis.models.project_config import ProjectConfig


class DataManager:
    def __init__(self, project: ProjectConfig):
        self.project = project
        self.files: list[DataFile] = []

    def set_project(self, project: ProjectConfig) -> None:
        self.project = project
        self.files = []

    def list_files(self) -> list[DataFile]:
        return list(self.files)

    def get_file(self, file_id: str) -> DataFile | None:
        return next((item for item in self.files if item.file_id == file_id), None)

    def get_config(self, file_id: str) -> DataFileConfig | None:
        runtime = self.get_file(file_id)
        if runtime:
            return runtime.config
        return next((config for config in self.project.data_files if config.file_id == file_id), None)

    def aliases(self) -> set[str]:
        return {data_file.config.alias for data_file in self.files}

    def add_csv(self, path: str | Path, alias: str | None = None, mapping: dict[str, str | None] | None = None) -> DataFile:
        if len(self.project.data_files) >= MAX_CSV_FILES:
            raise ValueError(f"最多只能加载 {MAX_CSV_FILES} 个 CSV 文件。")
        dataframe = read_csv(path)
        columns = [str(column) for column in dataframe.columns]
        alias = alias or self.project.allocate_alias()
        self.validate_alias(alias)
        file_id = self.project.allocate_file_id()
        color = DEFAULT_COLORS[(len(self.project.data_files)) % len(DEFAULT_COLORS)]
        config = DataFileConfig(
            file_id=file_id,
            path=str(Path(path)),
            alias=alias,
            color=color,
            column_mapping=mapping or detect_column_mapping(columns),
        )
        data_file = DataFile(config=config, dataframe=dataframe, columns=columns, row_count=len(dataframe))
        self.project.data_files.append(config)
        self.files.append(data_file)
        return data_file

    def add_loaded_config(self, config: DataFileConfig) -> DataFile:
        dataframe = read_csv(config.path)
        columns = [str(column) for column in dataframe.columns]
        config.missing = False
        data_file = DataFile(config=config, dataframe=dataframe, columns=columns, row_count=len(dataframe))
        self.files.append(data_file)
        return data_file

    def load_project_files(self) -> list[DataFileConfig]:
        self.files = []
        missing: list[DataFileConfig] = []
        for config in self.project.data_files:
            if not Path(config.path).exists():
                config.missing = True
                missing.append(config)
                self.files.append(DataFile(config=config, dataframe=None, columns=[], row_count=0))
                continue
            try:
                self.add_loaded_config(config)
            except Exception:
                config.missing = True
                missing.append(config)
                self.files.append(DataFile(config=config, dataframe=None, columns=[], row_count=0))
        return missing

    def remove_file(self, file_id: str) -> None:
        self.files = [item for item in self.files if item.file_id != file_id]
        self.project.data_files = [item for item in self.project.data_files if item.file_id != file_id]
        for tab in self.project.tabs:
            for plot in tab.plots:
                if getattr(plot, "plot_type", "") == "custom":
                    plot.curves = [curve for curve in plot.curves if curve.file_id != file_id]
                elif getattr(plot, "plot_type", "") == "preset":
                    plot.curve_visibility.pop(file_id, None)

    def validate_alias(self, alias: str, existing_file_id: str | None = None) -> None:
        alias = alias.strip()
        if not alias:
            raise ValueError("别名不能为空。")
        for data_file in self.files:
            if data_file.file_id != existing_file_id and data_file.config.alias == alias:
                raise ValueError(f"别名已存在：{alias}")

    def rename_file(self, file_id: str, alias: str) -> None:
        self.validate_alias(alias, existing_file_id=file_id)
        config = self.get_config(file_id)
        if not config:
            raise KeyError(file_id)
        config.alias = alias.strip()

    def set_color(self, file_id: str, color: str) -> None:
        config = self.get_config(file_id)
        if not config:
            raise KeyError(file_id)
        config.color = color

    def set_visible(self, file_id: str, visible: bool) -> None:
        config = self.get_config(file_id)
        if not config:
            raise KeyError(file_id)
        config.visible = visible
        config.visibility_version = self.project.next_visibility_version()
