from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from flightvis.core.data_manager import DataManager
from flightvis.core.project_manager import ProjectManager
from flightvis.io.column_detector import missing_required_mapping
from flightvis.io.csv_loader import read_csv
from flightvis.models.project_config import create_default_project
from flightvis.models.tab_config import create_custom_tab
from flightvis.ui.column_mapping_dialog import ColumnMappingDialog
from flightvis.ui.file_manager_dialog import FileManagerDialog
from flightvis.ui.import_files_dialog import ImportFilesDialog
from flightvis.ui.legend_bar import LegendBar
from flightvis.ui.new_tab_dialog import NewTabDialog
from flightvis.ui.tab_grid_widget import TabGridWidget
from flightvis.ui.trajectory_view import TrajectoryView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlightCSVVisualizer")
        self.project_manager = ProjectManager(create_default_project())
        self.data_manager = DataManager(self.project_manager.project)
        self.current_plot_cell = None
        self.tab_widgets: list[TabGridWidget] = []
        self.setup_ui()
        self.setup_actions()
        self.refresh_all_views()

    @property
    def project(self):
        return self.project_manager.project

    def setup_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        self.splitter = QSplitter(Qt.Horizontal)
        self.trajectory = TrajectoryView(self.data_manager, self.project_manager)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.setFixedSize(28, 24)
        self.add_tab_button.setToolTip("新建自定义选项卡")
        self.add_tab_button.clicked.connect(self.add_custom_tab)
        self.tabs.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)
        self.splitter.addWidget(self.trajectory)
        self.splitter.addWidget(self.tabs)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 3)
        self.legend = LegendBar(self.data_manager)
        layout.addWidget(self.splitter, 1)
        layout.addWidget(self.legend)
        self.setCentralWidget(central)
        self.legend.toggled.connect(self.on_global_visibility)
        self.legend.alias_changed.connect(self.on_alias_changed)
        self.legend.color_changed.connect(self.on_color_changed)

    def setup_actions(self) -> None:
        file_menu = self.menuBar().addMenu("文件")
        data_menu = self.menuBar().addMenu("数据")
        view_menu = self.menuBar().addMenu("视图")
        export_menu = self.menuBar().addMenu("导出")

        open_csv = file_menu.addAction("打开 CSV")
        load_project = file_menu.addAction("加载工程")
        save_project = file_menu.addAction("保存工程")
        save_project_as = file_menu.addAction("工程另存为")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("退出")
        manager = data_menu.addAction("数据文件管理")
        add_tab = view_menu.addAction("新建自定义选项卡")
        refresh = view_menu.addAction("刷新全部图窗")
        export_traj = export_menu.addAction("导出三维轨迹 PNG")
        export_plot = export_menu.addAction("导出当前二维图窗 PNG")

        open_csv.triggered.connect(self.open_csv_files)
        load_project.triggered.connect(self.load_project)
        save_project.triggered.connect(self.save_project)
        save_project_as.triggered.connect(self.save_project_as)
        exit_action.triggered.connect(self.close)
        manager.triggered.connect(self.open_file_manager)
        add_tab.triggered.connect(self.add_custom_tab)
        refresh.triggered.connect(self.refresh_all_views)
        export_traj.triggered.connect(self.export_trajectory)
        export_plot.triggered.connect(self.export_current_plot)

    def rebuild_tabs(self, preferred_tab_id: str | None = None) -> None:
        self.tabs.clear()
        self.tab_widgets = []
        for tab_config in self.project.tabs:
            widget = TabGridWidget(tab_config, self.data_manager, self.project_manager)
            widget.changed.connect(self.refresh_all_views)
            widget.plot_selected.connect(self.set_current_plot)
            self.tabs.addTab(widget, tab_config.name)
            self.tab_widgets.append(widget)
        for index, tab_config in enumerate(self.project.tabs):
            if tab_config.tab_type == "default":
                self.tabs.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, None)
        if preferred_tab_id:
            for index, tab_config in enumerate(self.project.tabs):
                if tab_config.tab_id == preferred_tab_id:
                    self.tabs.setCurrentIndex(index)
                    break

    def set_current_plot(self, cell) -> None:
        self.current_plot_cell = cell

    def refresh_all_views(self, preferred_tab_id: str | None = None) -> None:
        if preferred_tab_id is None and 0 <= self.tabs.currentIndex() < len(self.project.tabs):
            preferred_tab_id = self.project.tabs[self.tabs.currentIndex()].tab_id
        self.rebuild_tabs(preferred_tab_id)
        self.trajectory.refresh()
        self.legend.refresh()
        self.statusBar().showMessage(f"已加载 {len(self.data_manager.list_files())} 个 CSV 文件", 3000)

    def open_csv_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "打开 CSV 文件", str(Path.cwd()), "CSV 文件 (*.csv)")
        if not paths:
            return
        default_aliases = [self.project.allocate_alias() for _ in paths]
        dialog = ImportFilesDialog(paths, default_aliases, self.data_manager.aliases(), self)
        if not dialog.exec():
            self.project.next_file_alias_index -= len(paths)
            return
        for path, alias in zip(paths, dialog.aliases()):
            try:
                data_file = self.data_manager.add_csv(path, alias=alias)
                if missing_required_mapping(data_file.config.column_mapping):
                    mapping_dialog = ColumnMappingDialog(data_file.columns, data_file.config.column_mapping, f"列映射 - {alias}", self)
                    if mapping_dialog.exec():
                        data_file.config.column_mapping = mapping_dialog.mapping()
            except Exception as exc:
                QMessageBox.critical(self, "CSV 导入失败", str(exc))
        self.project_manager.mark_dirty()
        self.refresh_all_views()

    def open_file_manager(self) -> None:
        dialog = FileManagerDialog(self.data_manager, self.project, self)
        if dialog.exec():
            self.project_manager.mark_dirty()
            self.refresh_all_views()

    def on_global_visibility(self, file_id: str, visible: bool) -> None:
        self.data_manager.set_visible(file_id, visible)
        self.project_manager.mark_dirty()
        self.refresh_all_views()

    def on_alias_changed(self, file_id: str, alias: str) -> None:
        try:
            self.data_manager.rename_file(file_id, alias)
        except Exception as exc:
            QMessageBox.warning(self, "重命名失败", str(exc))
            return
        self.project_manager.mark_dirty()
        self.refresh_all_views()

    def on_color_changed(self, file_id: str, color: str) -> None:
        self.data_manager.set_color(file_id, color)
        self.project_manager.mark_dirty()
        self.refresh_all_views()

    def add_custom_tab(self) -> None:
        dialog = NewTabDialog({tab.name for tab in self.project.tabs}, self)
        if not dialog.exec():
            return
        name, rows, cols = dialog.values()
        tab_id = self.project.allocate_tab_id()
        self.project.tabs.append(create_custom_tab(tab_id, name, rows, cols))
        self.project_manager.mark_dirty()
        self.refresh_all_views(preferred_tab_id=tab_id)

    def close_tab(self, index: int) -> None:
        if index < 0 or index >= len(self.project.tabs):
            return
        tab_config = self.project.tabs[index]
        if tab_config.tab_type == "default":
            QMessageBox.information(self, "无法关闭", "基本状态量选项卡不能关闭。")
            return
        result = QMessageBox.question(self, "关闭选项卡", f"确定关闭“{tab_config.name}”吗？")
        if result != QMessageBox.Yes:
            return
        self.remove_tab_at(index)

    def remove_tab_at(self, index: int) -> None:
        if index < 0 or index >= len(self.project.tabs):
            return
        if self.project.tabs[index].tab_type == "default":
            return
        del self.project.tabs[index]
        self.project_manager.mark_dirty()
        self.refresh_all_views()

    def save_project(self) -> None:
        if not self.project.project_path:
            self.save_project_as()
            return
        try:
            self.project_manager.save()
            self.statusBar().showMessage("工程已保存", 3000)
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", str(exc))

    def save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "保存工程", "", "工程文件 (*.json)")
        if not path:
            return
        try:
            self.project_manager.save_as(path)
            self.statusBar().showMessage("工程已保存", 3000)
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", str(exc))

    def load_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "加载工程", "", "工程文件 (*.json)")
        if not path:
            return
        try:
            project = self.project_manager.load(path)
            self.data_manager.set_project(project)
            missing = self.data_manager.load_project_files()
            if missing:
                self.handle_missing_files(missing)
        except Exception as exc:
            QMessageBox.critical(self, "加载失败", str(exc))
            return
        self.refresh_all_views()

    def handle_missing_files(self, missing_configs) -> None:
        for config in missing_configs:
            answer = QMessageBox.question(
                self,
                "CSV 路径失效",
                f"找不到 {config.alias} 对应的文件：{config.path}\n是否重新定位？",
            )
            if answer != QMessageBox.Yes:
                continue
            path, _ = QFileDialog.getOpenFileName(self, f"重新定位 {config.alias}", "", "CSV 文件 (*.csv)")
            if not path:
                continue
            config.path = path
            try:
                self.data_manager.add_loaded_config(config)
            except Exception as exc:
                QMessageBox.warning(self, "重新定位失败", str(exc))

    def export_trajectory(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "导出三维轨迹", "", "PNG 图像 (*.png)")
        if path:
            self.trajectory.export_png(path)

    def export_current_plot(self) -> None:
        if not self.current_plot_cell:
            QMessageBox.information(self, "导出图窗", "请先点击一个二维图窗，再执行导出。")
            return
        path, _ = QFileDialog.getSaveFileName(self, "导出图窗", "", "PNG 图像 (*.png)")
        if path:
            self.current_plot_cell.export_png(path)

    def closeEvent(self, event) -> None:
        if self.project_manager.dirty:
            result = QMessageBox.question(self, "未保存的更改", "关闭前是否保存工程？")
            if result == QMessageBox.Yes:
                self.save_project()
        super().closeEvent(event)
