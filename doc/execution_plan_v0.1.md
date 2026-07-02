# 飞行器 CSV 数据可视化软件执行计划 v0.1

面向 Codex / 智能体 / 开发者的工程实现计划

| 项目 | 内容 |
|---|---|
| 文档版本 | v0.1 |
| 依据文档 | 《飞行器 CSV 数据可视化软件设计文档 v0.1》 |
| 目标 | 指导智能体分阶段实现第一版 MVP |
| 建议技术栈 | Python + PySide6 + pandas + NumPy + Matplotlib + PyInstaller |
| 目标平台 | Windows 桌面程序，开发阶段可跨平台运行 |
| 交付形态 | 源代码工程 + 可双击运行的打包程序 |

---

## 0. 实施原则

第一版开发目标不是做成大型数据分析平台，而是先实现一个稳定、清晰、可扩展的桌面可视化工具。开发时应优先保证：

1. 主界面和交互流程稳定。
2. CSV 多文件加载和列映射可靠。
3. 默认 3×3 图窗行为简单、固定、可预测。
4. 自定义图窗具备横向对比、纵向对比和手动添加曲线能力。
5. 工程 JSON 能完整保存和恢复用户配置。
6. 可见性规则严格采用“最后一次操作优先”。
7. 代码结构清晰，后续可替换绘图库或扩展单位转换、滤波、动画等功能。

开发智能体不得在第一版中主动加入设计文档未要求的大型功能，例如地图背景、实时数据流、数据库管理、飞行器三维实体、复杂滤波器、在线同步等。

---

## 1. 技术路线

### 1.1 技术栈选择

| 模块 | 推荐技术 | 用途 |
|---|---|---|
| GUI 框架 | PySide6 | 主窗口、选项卡、弹窗、表格、按钮、菜单 |
| CSV 读取 | pandas | 读取 CSV、管理列名、保存 DataFrame |
| 数值处理 | NumPy | 抽稀、范围计算、数组处理 |
| 二维绘图 | Matplotlib | 嵌入式 2D 曲线绘制、PNG 导出 |
| 三维绘图 | Matplotlib mplot3d | 三维轨迹绘制、旋转、缩放、PNG 导出 |
| 配置保存 | JSON + dataclasses | 工程文件保存与恢复 |
| 异步加载 | QThread 或 QRunnable | 读取大 CSV 时避免界面冻结 |
| 自动保存 | QTimer | 配置变更防抖保存 |
| 打包 | PyInstaller | 生成可双击运行程序 |
| 测试 | pytest | 数据结构、列识别、可见性逻辑、JSON 序列化测试 |

### 1.2 为什么第一版使用 Matplotlib

第一版数据规模为单 CSV 一般几千到几万行，极端不超过 100000 行，同时加载文件默认最多 10 个。Matplotlib 能满足第一版需求，并且：

- 与 PySide6 集成方式成熟；
- 支持二维和三维绘图；
- 支持直接导出 PNG；
- 智能体实现难度低；
- 后续可在绘图层替换为 PyQtGraph、VisPy 或 PyVista。

### 1.3 运行方式

开发阶段：

```bash
python main.py
```

发布阶段：

```bash
pyinstaller --noconfirm --windowed --clean --name FlightCSVVisualizer main.py
```

推荐优先使用 PyInstaller 文件夹模式发布，而不是单文件模式。文件夹模式启动速度更快，资源管理更清晰，后续更新更方便。

---

## 2. 推荐工程结构

建议采用 `src` 布局，方便测试和打包。

```text
flight_csv_visualizer/
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
│
├── examples/
│   └── sample.csv
│
├── scripts/
│   ├── run_dev.bat
│   ├── build_windows.bat
│   └── clean_build.bat
│
├── src/
│   └── flightvis/
│       ├── __init__.py
│       ├── app.py
│       ├── constants.py
│       ├── settings.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── data_file.py
│       │   ├── column_mapping.py
│       │   ├── plot_config.py
│       │   ├── curve_config.py
│       │   ├── tab_config.py
│       │   ├── project_config.py
│       │   └── visibility.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── data_manager.py
│       │   ├── project_manager.py
│       │   ├── visibility_manager.py
│       │   └── event_bus.py
│       │
│       ├── io/
│       │   ├── __init__.py
│       │   ├── csv_loader.py
│       │   ├── column_detector.py
│       │   ├── project_io.py
│       │   └── export_image.py
│       │
│       ├── plotting/
│       │   ├── __init__.py
│       │   ├── mpl_canvas.py
│       │   ├── plot_renderer.py
│       │   ├── trajectory_renderer.py
│       │   ├── downsample.py
│       │   └── style.py
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── trajectory_view.py
│       │   ├── legend_bar.py
│       │   ├── file_manager_dialog.py
│       │   ├── import_files_dialog.py
│       │   ├── column_mapping_dialog.py
│       │   ├── new_tab_dialog.py
│       │   ├── tab_grid_widget.py
│       │   ├── plot_cell_base.py
│       │   ├── preset_plot_cell.py
│       │   ├── custom_plot_cell.py
│       │   ├── preset_plot_settings_dialog.py
│       │   ├── custom_plot_settings_dialog.py
│       │   ├── curve_manager_dialog.py
│       │   ├── display_settings_widget.py
│       │   ├── compare_mode_widget.py
│       │   ├── add_curve_widget.py
│       │   └── widgets/
│       │       ├── __init__.py
│       │       ├── flow_layout.py
│       │       ├── color_button.py
│       │       └── labeled_combo.py
│       │
│       └── resources/
│           ├── icons/
│           └── app.qss
│
└── tests/
    ├── test_column_detector.py
    ├── test_downsample.py
    ├── test_visibility_manager.py
    ├── test_project_serialization.py
    └── test_data_manager.py
```

---

## 3. 依赖配置

### 3.1 requirements.txt

```text
PySide6
pandas
numpy
matplotlib
pytest
```

第一版尽量不要引入过多依赖。JSON 序列化可以使用 Python 标准库 `json` 和 `dataclasses` 完成。

### 3.2 pyproject.toml 建议

```toml
[project]
name = "flight-csv-visualizer"
version = "0.1.0"
description = "Lightweight desktop visualizer for flight CSV data"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### 3.3 main.py

`main.py` 应尽量简短，只负责启动应用。

```python
import sys
from PySide6.QtWidgets import QApplication
from flightvis.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 4. 核心数据模型

数据模型应放在 `src/flightvis/models/` 中。第一版建议使用 `dataclasses`，每个模型提供 `to_dict()` 和 `from_dict()`，确保 JSON 保存和加载稳定。

### 4.1 可见性模型

可见性必须支持“最后一次操作优先”。推荐使用单调递增的整数版本号，而不是时间戳。整数版本号更容易测试，也不会受系统时间精度影响。

```python
from dataclasses import dataclass

@dataclass
class VisibilityState:
    visible: bool = True
    version: int = 0
```

项目中维护一个全局可见性操作计数器：

```python
project.visibility_counter += 1
```

每次用户在公共图例或曲线窗口执行显示/隐藏操作时，相关对象的 `version` 更新为最新计数器。

### 4.2 DataFileConfig

保存 CSV 文件的工程配置，不保存 DataFrame 本体。

```python
@dataclass
class DataFileConfig:
    file_id: str
    path: str
    alias: str
    color: str
    visible: bool = True
    visibility_version: int = 0
    column_mapping: dict[str, str | None] = field(default_factory=dict)
```

运行时对象：

```python
@dataclass
class DataFile:
    config: DataFileConfig
    dataframe: pandas.DataFrame
    columns: list[str]
    row_count: int
```

JSON 中只保存 `DataFileConfig`，加载工程时根据 `path` 重新读取 CSV。

### 4.3 ColumnMapping

标准字段如下：

```python
STANDARD_MAPPING_KEYS = [
    "time",
    "x", "y", "z",
    "vx", "vy", "vz",
    "roll", "pitch", "yaw",
    "wx", "wy", "wz",
]
```

示例映射：

```json
{
  "time": "time",
  "x": "x",
  "y": "y",
  "z": "z",
  "vx": "vx",
  "vy": "vy",
  "vz": "vz",
  "roll": "phi",
  "pitch": "theta",
  "yaw": "psi",
  "wx": "wx",
  "wy": "wy",
  "wz": "wz"
}
```

### 4.4 DisplayConfig

图窗外观设置。

```python
@dataclass
class DisplayConfig:
    x_label: str = "time"
    y_label: str = "value"
    show_grid: bool = True
    show_local_legend: bool = False
    x_range: tuple[float, float] | None = None
    y_range: tuple[float, float] | None = None
    line_width: float = 1.5
    line_style: str = "-"
```

### 4.5 PresetPlotConfig

默认 3×3 图窗使用预设图窗配置，不保存完整 curves 列表。

```python
@dataclass
class PresetPlotConfig:
    plot_id: str
    plot_type: str = "preset"
    preset_variable: str = "vx"
    row: int = 0
    col: int = 0
    title: str = ""
    display: DisplayConfig = field(default_factory=DisplayConfig)
    curve_visibility: dict[str, VisibilityState] = field(default_factory=dict)
```

`curve_visibility` 的 key 是 `file_id`，用于保存该预设图窗内某个文件曲线的局部显示状态。

### 4.6 CurveConfig

自定义图窗才保存完整曲线列表。

```python
@dataclass
class CurveConfig:
    curve_id: str
    source: str  # horizontal_compare / vertical_compare / manual
    file_id: str
    x_column: str
    y_column: str
    label: str
    use_file_color: bool = True
    color: str | None = None
    line_width: float = 1.5
    line_style: str = "-"
    visible: bool = True
    visibility_version: int = 0
```

### 4.7 HorizontalCompareConfig

```python
@dataclass
class HorizontalCompareConfig:
    enabled: bool = False
    compare_by: str = "mapped_variable"  # mapped_variable / actual_column
    x_mode: str = "mapped_time"          # mapped_time / actual_column
    x_column: str = "time"
    y_variable: str | None = None
    included_file_ids: list[str] | str = "all"
    auto_include_new_files: bool = True
    missing_column_policy: str = "skip_with_warning"
```

### 4.8 VerticalCompareConfig

```python
@dataclass
class VerticalCompareConfig:
    enabled: bool = False
    file_id: str | None = None
    x_column: str = "time"
    y_columns: list[str] = field(default_factory=list)
    color_strategy: str = "auto_by_variable"
    show_local_legend: bool = True
    on_file_changed: str = "reuse_columns_if_available"
    missing_column_policy: str = "keep_available_and_warn"
```

### 4.9 CustomPlotConfig

```python
@dataclass
class CustomPlotConfig:
    plot_id: str
    plot_type: str = "custom"
    plot_mode: str = "manual"  # horizontal_compare / vertical_compare / manual / mixed
    row: int = 0
    col: int = 0
    title: str = "未配置图窗"
    display: DisplayConfig = field(default_factory=DisplayConfig)
    horizontal_compare: HorizontalCompareConfig = field(default_factory=HorizontalCompareConfig)
    vertical_compare: VerticalCompareConfig = field(default_factory=VerticalCompareConfig)
    curves: list[CurveConfig] = field(default_factory=list)
```

### 4.10 TabConfig

```python
@dataclass
class TabConfig:
    tab_id: str
    name: str
    tab_type: str  # default / custom
    rows: int
    cols: int
    plots: list[PresetPlotConfig | CustomPlotConfig]
```

### 4.11 ProjectConfig

```python
@dataclass
class ProjectConfig:
    project_version: str = "0.1"
    project_name: str = "untitled"
    project_path: str | None = None
    last_modified: str | None = None
    autosave_enabled: bool = True
    visibility_counter: int = 0
    next_file_alias_index: int = 1
    window: dict = field(default_factory=dict)
    data_files: list[DataFileConfig] = field(default_factory=list)
    trajectory_view: dict = field(default_factory=dict)
    tabs: list[TabConfig] = field(default_factory=list)
```

---

## 5. 关键业务逻辑

### 5.1 CSV 加载流程

```text
用户点击“打开 CSV”
        ↓
QFileDialog 选择一个或多个 CSV
        ↓
弹出 ImportFilesDialog
        ↓
自动分配别名 dataN，用户可修改
        ↓
DataManager 读取 CSV
        ↓
ColumnDetector 自动识别列映射
        ↓
若关键列缺失，弹出 ColumnMappingDialog
        ↓
创建 DataFileConfig 和 DataFile
        ↓
更新公共图例、三维轨迹、默认 3×3 图窗、自定义图窗
        ↓
ProjectManager.mark_dirty("import_csv")
```

### 5.2 默认别名规则

`DataManager` 维护 `next_file_alias_index`。

```python
def allocate_default_alias(project: ProjectConfig) -> str:
    alias = f"data{project.next_file_alias_index}"
    project.next_file_alias_index += 1
    return alias
```

删除文件后不复用编号。例如加载 data1、data2、data3，删除 data2 后再加载新文件，新文件默认为 data4。

### 5.3 自动列识别

`column_detector.py` 负责自动识别。

优先级示例：

```python
CANDIDATES = {
    "time": ["time", "t", "Time", "timestamp"],
    "x": ["x", "X", "pos_x", "position_x"],
    "y": ["y", "Y", "pos_y", "position_y"],
    "z": ["z", "Z", "pos_z", "position_z", "altitude"],
    "vx": ["vx", "v_x", "vel_x", "velocity_x"],
    "vy": ["vy", "v_y", "vel_y", "velocity_y"],
    "vz": ["vz", "v_z", "vel_z", "velocity_z"],
    "roll": ["phi", "roll", "att_x"],
    "pitch": ["theta", "pitch", "att_y"],
    "yaw": ["psi", "yaw", "att_z"],
    "wx": ["wx", "p", "omega_x", "ang_vel_x"],
    "wy": ["wy", "q", "omega_y", "ang_vel_y"],
    "wz": ["wz", "r", "omega_z", "ang_vel_z"],
}
```

识别策略：

1. 先精确匹配。
2. 再大小写不敏感匹配。
3. 再去除 `_`、`-` 后匹配。
4. 多个候选命中时使用候选列表中优先级最高的列。
5. 无法识别时返回 `None`，由列映射窗口处理。

### 5.4 列映射窗口

控件选择：

| 功能 | 控件 |
|---|---|
| 标准字段标签 | QLabel |
| 实际列选择 | QComboBox |
| 可选无映射 | QComboBox 第一项为“无” |
| 确定/取消 | QPushButton |
| 多文件映射 | 第一版可逐个文件弹窗 |

当默认图窗所需列缺失时，不阻止文件加载；仅在绘图时跳过缺失曲线。

### 5.5 可见性最后操作优先

全局公共图例与图窗内部曲线窗口采用“最后一次操作优先”。推荐使用版本号实现。

#### 5.5.1 公共图例操作

当用户在底部公共图例中显示/隐藏某个文件：

```python
project.visibility_counter += 1
file.config.visible = target_visible
file.config.visibility_version = project.visibility_counter
refresh_all_plots()
mark_dirty("global_visibility_changed")
```

#### 5.5.2 默认图窗局部曲线操作

当用户在默认图窗的曲线窗口中显示/隐藏某个文件对应曲线：

```python
project.visibility_counter += 1
plot.curve_visibility[file_id] = VisibilityState(
    visible=target_visible,
    version=project.visibility_counter,
)
refresh_plot(plot_id)
mark_dirty("preset_curve_visibility_changed")
```

#### 5.5.3 自定义图窗曲线操作

当用户在自定义图窗曲线管理窗口中显示/隐藏某条曲线：

```python
project.visibility_counter += 1
curve.visible = target_visible
curve.visibility_version = project.visibility_counter
refresh_plot(plot_id)
mark_dirty("custom_curve_visibility_changed")
```

#### 5.5.4 生效可见性计算

默认图窗：

```python
def effective_preset_curve_visible(file_config, local_visibility):
    if local_visibility is None:
        return file_config.visible

    if local_visibility.version > file_config.visibility_version:
        return local_visibility.visible
    return file_config.visible
```

自定义图窗：

```python
def effective_custom_curve_visible(file_config, curve):
    if curve.visibility_version > file_config.visibility_version:
        return curve.visible
    return file_config.visible
```

三维轨迹没有局部曲线窗口，仅使用文件全局可见性：

```python
def trajectory_visible(file_config):
    return file_config.visible
```

---

## 6. 主界面实现方案

### 6.1 MainWindow

`MainWindow` 继承 `QMainWindow`。

核心组成：

```text
QMainWindow
├── menuBar / toolBar
├── centralWidget
│   └── QVBoxLayout
│       ├── main_splitter: QSplitter(Qt.Horizontal)
│       │   ├── TrajectoryView
│       │   └── QTabWidget
│       └── LegendBar
└── statusBar 可省略或仅用于临时提示
```

### 6.2 控件选择

| 区域 | 控件 |
|---|---|
| 主窗口 | QMainWindow |
| 左右分栏 | QSplitter(Qt.Horizontal) |
| 右侧选项卡 | QTabWidget |
| 默认/自定义图窗网格 | QGridLayout |
| 每个图窗区域 | QWidget + QVBoxLayout + FigureCanvas + 按钮层 |
| 底部公共图例 | QScrollArea + FlowLayout 或 QHBoxLayout |
| 菜单栏 | QMenuBar + QAction |
| 弹窗 | QDialog |
| 表格 | QTableWidget |
| 文件选择 | QFileDialog |
| 颜色选择 | QColorDialog |
| 自动保存 | QTimer |

### 6.3 菜单动作

| 菜单 | QAction | 绑定方法 |
|---|---|---|
| 文件 | 打开 CSV | `MainWindow.open_csv_files()` |
| 文件 | 加载工程 | `MainWindow.load_project()` |
| 文件 | 保存工程 | `MainWindow.save_project()` |
| 文件 | 工程另存为 | `MainWindow.save_project_as()` |
| 文件 | 退出 | `MainWindow.close()` |
| 数据 | 数据文件管理 | `MainWindow.open_file_manager()` |
| 视图 | 刷新全部图窗 | `MainWindow.refresh_all_views()` |
| 导出 | 导出三维轨迹 PNG | `TrajectoryView.export_png()` |
| 导出 | 导出当前二维图窗 PNG | 由当前选中图窗处理 |

---

## 7. 图窗体系实现

### 7.1 图窗基类 PlotCellBase

所有二维图窗区域使用统一基类。

```text
PlotCellBase(QWidget)
├── title_label
├── Matplotlib FigureCanvas
├── button_row
│   ├── curve_button
│   └── settings_button
└── refresh()
```

右下角固定两个小按钮：

```text
[曲线] [设置]
```

### 7.2 PresetPlotCell

默认 3×3 图窗使用 `PresetPlotCell`。

特性：

- 固定变量，不允许改绘图模式。
- 不允许添加或删除曲线。
- `[设置]` 只打开 `PresetPlotSettingsDialog`。
- `[曲线]` 只打开简化版 `CurveManagerDialog`，用于显示/隐藏该图窗内各文件曲线。

默认 9 个图窗：

| 位置 | preset_variable | 标题 | Y 轴标签 |
|---|---|---|---|
| row 0 col 0 | vx | X方向速度 | vx |
| row 0 col 1 | vy | Y方向速度 | vy |
| row 0 col 2 | vz | Z方向速度 | vz |
| row 1 col 0 | roll | 滚转角 | phi / rad |
| row 1 col 1 | pitch | 俯仰角 | theta / rad |
| row 1 col 2 | yaw | 偏航角 | psi / rad |
| row 2 col 0 | wx | X轴角速度 | wx / rad/s |
| row 2 col 1 | wy | Y轴角速度 | wy / rad/s |
| row 2 col 2 | wz | Z轴角速度 | wz / rad/s |

注意：`roll/pitch/yaw` 是标准变量含义，实际列由 `column_mapping` 决定，样例 CSV 中对应 `phi/theta/psi`。

### 7.3 CustomPlotCell

自定义选项卡中的图窗使用 `CustomPlotCell`。

特性：

- 支持横向对比。
- 支持纵向对比。
- 支持手动添加单独曲线。
- `[设置]` 打开完整多选项卡设置窗口。
- `[曲线]` 打开完整曲线管理窗口。

### 7.4 自定义图窗设置窗口

`CustomPlotSettingsDialog` 使用 `QTabWidget` 分页。

```text
CustomPlotSettingsDialog
├── 绘图模式 CompareModeWidget
├── 绘图细节 DisplaySettingsWidget
└── 添加曲线 AddCurveWidget
```

#### 绘图模式页

控件选择：

| 功能 | 控件 |
|---|---|
| 模式选择 | QRadioButton + QButtonGroup |
| 横向/纵向配置区域切换 | QStackedWidget |
| 文件勾选 | QListWidget 或 QTableWidget + checkbox |
| Y 变量选择 | QComboBox |
| 多列选择 | QListWidget + checkbox |
| 生成按钮 | QPushButton |

横向对比设置：

```text
模式：横向对比
对比方式：按标准变量映射 / 按实际列名
X 轴：使用映射 time / 指定实际列名
Y 轴变量或列名：下拉选择
参与文件：多选
自动包含后续加载 CSV：checkbox
生成/刷新图窗曲线：button
```

纵向对比设置：

```text
模式：纵向对比
数据文件：下拉选择
X 轴列：下拉选择
Y 轴列：多选列表
颜色策略：变量自动颜色 / 文件颜色
显示局部图例：checkbox，默认开启
生成/刷新图窗曲线：button
```

#### 绘图细节页

使用 `DisplaySettingsWidget`，默认图窗和自定义图窗可复用该控件。

```text
图窗标题
X轴标签
Y轴标签
显示网格
显示局部图例
X轴范围：自动 / 手动
Y轴范围：自动 / 手动
默认线宽
默认线型
```

#### 添加曲线页

使用 `AddCurveWidget`。

```text
数据文件
X轴列
Y轴列
曲线名称
颜色模式：文件颜色 / 自定义颜色
线宽
线型
添加到当前图窗
```

添加成功后不在此窗口展示完整列表，只提示用户可通过 `[曲线]` 按钮管理。

### 7.5 默认图窗设置窗口

`PresetPlotSettingsDialog` 只显示绘图细节，不显示绘图模式和添加曲线。

```text
图窗标题
X轴标签
Y轴标签
显示网格
显示局部图例
X轴范围
Y轴范围
默认线宽
默认线型
```

### 7.6 曲线管理窗口

`CurveManagerDialog` 根据图窗类型显示不同功能。

#### 默认图窗曲线管理

只允许：

- 显示/隐藏当前图窗中某个文件对应的曲线；
- 全选；
- 全不选；
- 恢复默认。

表格列：

| 显示 | 文件别名 | 实际 X 列 | 实际 Y 列 |
|---|---|---|---|

不允许：

- 添加曲线；
- 删除曲线；
- 修改 X/Y 列；
- 修改颜色；
- 修改线宽；
- 排序。

#### 自定义图窗曲线管理

允许：

- 显示/隐藏；
- 删除曲线；
- 清空曲线；
- 上移/下移；
- 修改颜色模式；
- 修改颜色；
- 修改线宽；
- 修改线型。

表格列：

| 显示 | 曲线名 | 来源 | 文件 | X列 | Y列 | 颜色模式 | 颜色 | 线宽 | 线型 |
|---|---|---|---|---|---|---|---|---|---|

---

## 8. 绘图实现方案

### 8.1 MatplotlibCanvas

`plotting/mpl_canvas.py` 提供统一画布类。

```python
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, projection: str | None = None):
        self.figure = Figure(figsize=(4, 3), tight_layout=True)
        if projection == "3d":
            self.ax = self.figure.add_subplot(111, projection="3d")
        else:
            self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)
```

### 8.2 二维绘图渲染器

`plot_renderer.py` 只负责根据配置和数据绘图，不直接操作 UI 控件。

```python
def render_preset_plot(ax, plot_config, data_manager, project_config):
    ax.clear()
    for data_file in data_manager.files:
        x_col, y_col = resolve_preset_columns(data_file, plot_config.preset_variable)
        if not x_col or not y_col:
            continue

        local_vis = plot_config.curve_visibility.get(data_file.config.file_id)
        if not effective_preset_curve_visible(data_file.config, local_vis):
            continue

        df = data_file.dataframe
        ax.plot(
            df[x_col],
            df[y_col],
            label=data_file.config.alias,
            color=data_file.config.color,
            linewidth=plot_config.display.line_width,
            linestyle=plot_config.display.line_style,
        )

    apply_display_settings(ax, plot_config.display, plot_config.title)
```

自定义图窗：

```python
def render_custom_plot(ax, plot_config, data_manager, project_config):
    ax.clear()
    for curve in plot_config.curves:
        data_file = data_manager.get_file(curve.file_id)
        if data_file is None:
            continue
        if not effective_custom_curve_visible(data_file.config, curve):
            continue
        if curve.x_column not in data_file.columns or curve.y_column not in data_file.columns:
            continue

        color = data_file.config.color if curve.use_file_color else curve.color
        ax.plot(
            data_file.dataframe[curve.x_column],
            data_file.dataframe[curve.y_column],
            label=curve.label,
            color=color,
            linewidth=curve.line_width,
            linestyle=curve.line_style,
        )

    apply_display_settings(ax, plot_config.display, plot_config.title)
```

### 8.3 纵向对比曲线生成

```python
def generate_vertical_curves(plot_config, data_file):
    curves = []
    missing = []

    if plot_config.vertical_compare.x_column not in data_file.columns:
        return [], [plot_config.vertical_compare.x_column]

    for y_col in plot_config.vertical_compare.y_columns:
        if y_col not in data_file.columns:
            missing.append(y_col)
            continue
        curves.append(CurveConfig(
            curve_id=new_curve_id(),
            source="vertical_compare",
            file_id=data_file.config.file_id,
            x_column=plot_config.vertical_compare.x_column,
            y_column=y_col,
            label=f"{data_file.config.alias} / {y_col}",
            use_file_color=False,
            color=assign_variable_color(y_col),
        ))

    return curves, missing
```

切换文件时，复用原先 `y_columns`。若新文件中存在这些列则自动绘制；若部分缺失则保留可用列并提示；若全部缺失则等待用户重新选择。

### 8.4 横向对比曲线生成

```python
def generate_horizontal_curves(plot_config, data_manager):
    curves = []
    warnings = []
    included = resolve_included_files(plot_config.horizontal_compare, data_manager)

    for data_file in included:
        x_col = resolve_horizontal_x_column(plot_config.horizontal_compare, data_file)
        y_col = resolve_horizontal_y_column(plot_config.horizontal_compare, data_file)

        if not x_col or not y_col:
            warnings.append(f"{data_file.config.alias} 缺少所需列")
            continue

        curves.append(CurveConfig(
            curve_id=new_curve_id(),
            source="horizontal_compare",
            file_id=data_file.config.file_id,
            x_column=x_col,
            y_column=y_col,
            label=data_file.config.alias,
            use_file_color=True,
        ))

    return curves, warnings
```

横向对比默认关闭局部图例，依赖底部公共图例。

### 8.5 三维轨迹绘制

`trajectory_renderer.py` 负责三维轨迹。

```python
def render_trajectory(ax, data_manager, trajectory_config):
    ax.clear()
    for data_file in data_manager.files:
        if not data_file.config.visible:
            continue

        mapping = data_file.config.column_mapping
        x_col, y_col, z_col = mapping.get("x"), mapping.get("y"), mapping.get("z")
        if not all([x_col, y_col, z_col]):
            continue
        if x_col not in data_file.columns or y_col not in data_file.columns or z_col not in data_file.columns:
            continue

        x, y, z = downsample_xyz(
            data_file.dataframe[x_col].to_numpy(),
            data_file.dataframe[y_col].to_numpy(),
            data_file.dataframe[z_col].to_numpy(),
            max_points=trajectory_config.get("max_points", 50000),
        )
        ax.plot(x, y, z, label=data_file.config.alias, color=data_file.config.color)
        draw_start_end_markers(ax, x, y, z, data_file.config.color)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.grid(trajectory_config.get("show_grid", True))
    set_equal_3d_axes(ax)
```

三维轨迹只受公共图例文件级可见性控制，不受单个二维图窗曲线窗口影响。

### 8.6 抽稀策略

`downsample.py`：

```python
def downsample_indices(n: int, max_points: int) -> np.ndarray:
    if n <= max_points:
        return np.arange(n)
    step = int(np.ceil(n / max_points))
    return np.arange(0, n, step)
```

第一版采用均匀抽稀。后续可升级为 Largest Triangle Three Buckets 等保形抽稀算法。

---

## 9. 底部公共图例实现

### 9.1 LegendBar

`LegendBar` 位于主界面底部，用于显示和管理所有 CSV 文件。

建议结构：

```text
LegendBar(QWidget)
└── QScrollArea
    └── FlowLayout
        ├── LegendItemWidget(data1)
        ├── LegendItemWidget(data2)
        └── LegendItemWidget(data3)
```

### 9.2 LegendItemWidget

每个图例项包含：

| 元素 | 控件 |
|---|---|
| 颜色块 | QPushButton 或自定义 ColorButton |
| 文件别名 | QLabel |
| 显示/隐藏状态 | QCheckBox 或可点击整体区域 |
| 右键菜单 | QMenu |

右键菜单：

```text
重命名
修改颜色
显示/隐藏
重新设置列映射
从工程中移除
```

### 9.3 交互规则

- 单击或勾选：切换该文件全局显示状态。
- 修改颜色：更新 `DataFileConfig.color`，所有使用文件颜色的曲线自动刷新。
- 重命名：更新 `DataFileConfig.alias`，曲线标签和公共图例刷新。
- 删除文件：从 DataManager 移除，工程中保留或删除配置取决于文件管理操作；第一版建议从当前工程移除。

---

## 10. 工程 JSON 保存与加载

### 10.1 ProjectManager

`ProjectManager` 负责：

- 创建新工程；
- 保存工程；
- 工程另存为；
- 加载工程；
- 自动保存；
- dirty 状态管理；
- visibility_counter 管理。

### 10.2 自动保存策略

采用防抖保存：

```python
class ProjectManager(QObject):
    def __init__(self):
        self.dirty = False
        self.autosave_timer = QTimer()
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self.autosave_now)

    def mark_dirty(self, reason: str):
        self.dirty = True
        self.autosave_timer.start(1000)
```

保存规则：

- 重要配置变化后调用 `mark_dirty()`。
- 1 秒内连续修改只写一次 JSON。
- 不保存鼠标缩放、平移、旋转等临时视图状态。
- 如果已有工程路径，自动保存到该路径。
- 如果没有工程路径，可保存到临时 autosave 文件，并在关闭时提示用户保存正式工程。

### 10.3 原子写入

写 JSON 时使用临时文件，避免保存中断导致工程文件损坏。

```python
def save_json_atomic(path, data):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)
```

### 10.4 路径失效处理

加载工程时，如果 CSV 路径不存在：

1. 弹出提示。
2. 允许用户重新定位该 CSV。
3. 如果跳过，则保留该文件配置但不绘制。
4. 重新定位成功后，恢复别名、颜色、列映射和曲线配置。

实现上可在 `DataManager.load_from_project()` 中记录 missing 文件列表，由 UI 弹窗处理。

---

## 11. 文件管理与导入窗口

### 11.1 ImportFilesDialog

用户选择 CSV 后，弹出导入窗口。

表格列：

| 文件路径 | 默认别名 | 用户别名 | 状态 |
|---|---|---|---|

控件：

| 功能 | 控件 |
|---|---|
| 文件列表 | QTableWidget |
| 别名编辑 | QTableWidgetItem 可编辑 |
| 自动命名 | QPushButton |
| 使用文件名 | QPushButton |
| 确认导入 | QPushButton |
| 取消 | QPushButton |

校验：

- 别名不能为空；
- 当前工程内唯一；
- 新导入文件之间也不能重复；
- 重复时高亮单元格并禁止确认。

### 11.2 FileManagerDialog

数据文件管理窗口。

功能：

| 功能 | 控件/方式 |
|---|---|
| 查看文件路径 | QTableWidget |
| 修改别名 | 可编辑单元格或按钮 |
| 修改颜色 | ColorButton + QColorDialog |
| 显示/隐藏 | QCheckBox |
| 修改列映射 | 打开 ColumnMappingDialog |
| 移除文件 | QPushButton |

移除文件后：

- 从 DataManager 删除运行时 DataFile；
- 从 ProjectConfig 删除 DataFileConfig；
- 刷新公共图例、三维轨迹、默认图窗、自定义图窗；
- 自定义图窗中引用该文件的曲线可以标记为 invalid 或删除。第一版建议弹窗询问：删除相关曲线或保留为失效曲线。为简化 MVP，可直接删除相关曲线。

---

## 12. 自定义选项卡实现

### 12.1 新建选项卡

点击 QTabWidget 右侧 `+` 按钮或工具栏按钮。

弹出 `NewTabDialog`。

字段：

| 字段 | 控件 | 限制 |
|---|---|---|
| 选项卡名称 | QLineEdit | 非空、当前工程内唯一 |
| 行数 | QSpinBox | 1 到 5 |
| 列数 | QSpinBox | 1 到 5 |

确认后：

- 创建 `TabConfig(tab_type="custom")`；
- 创建 rows × cols 个 `CustomPlotConfig`；
- 每个自定义图窗初始为空，标题为“未配置图窗”；
- 刷新 QTabWidget；
- `mark_dirty("add_custom_tab")`。

### 12.2 TabGridWidget

`TabGridWidget` 根据 `TabConfig` 创建网格。

```python
class TabGridWidget(QWidget):
    def __init__(self, tab_config, data_manager, project_manager):
        self.layout = QGridLayout(self)
        for plot in tab_config.plots:
            if plot.plot_type == "preset":
                cell = PresetPlotCell(plot, ...)
            else:
                cell = CustomPlotCell(plot, ...)
            self.layout.addWidget(cell, plot.row, plot.col)
```

自定义 5×5 时图窗可能较小，建议使用 `QScrollArea` 包裹自定义选项卡内容。

---

## 13. 信号与刷新机制

### 13.1 推荐信号

可以在 `core/event_bus.py` 中定义统一事件总线，或在 MainWindow 内协调。

推荐信号：

```python
class EventBus(QObject):
    data_files_changed = Signal()
    file_visibility_changed = Signal(str)
    file_color_changed = Signal(str)
    file_alias_changed = Signal(str)
    plot_config_changed = Signal(str)
    curve_visibility_changed = Signal(str)
    project_loaded = Signal()
```

### 13.2 刷新原则

| 事件 | 刷新范围 |
|---|---|
| 添加/删除 CSV | 公共图例、三维轨迹、所有图窗 |
| 修改文件颜色 | 公共图例、三维轨迹、所有使用文件颜色的曲线 |
| 修改文件别名 | 公共图例、曲线标签、局部图例 |
| 公共图例显示/隐藏 | 三维轨迹、所有图窗 |
| 默认图窗局部显示/隐藏 | 当前默认图窗 |
| 自定义图窗曲线变更 | 当前自定义图窗 |
| 图窗绘图细节变更 | 当前图窗 |
| 加载工程 | 全部重建 |

第一版可以简单地在多数情况下刷新所有图窗，以降低实现复杂度。性能不足时再做局部刷新优化。

---

## 14. 导出功能

第一版只实现：

1. 单个二维图窗导出 PNG。
2. 三维轨迹导出 PNG。

### 14.1 二维图窗导出

在 PlotCellBase 增加方法：

```python
def export_png(self, path: str):
    self.canvas.figure.savefig(path, dpi=200, bbox_inches="tight")
```

入口可以放在：

- 图窗右键菜单；
- 设置窗口中的导出按钮；
- 主菜单“导出当前图窗”。

### 14.2 三维轨迹导出

`TrajectoryView.export_png()`：

```python
def export_png(self, path: str):
    self.canvas.figure.savefig(path, dpi=200, bbox_inches="tight")
```

第一版不要求整页导出、批量导出。

---

## 15. 测试计划

### 15.1 单元测试

必须优先测试非 UI 逻辑。

| 测试文件 | 测试内容 |
|---|---|
| test_column_detector.py | time/x/y/z/vx/phi/wx 等列自动识别 |
| test_downsample.py | 不超过 max_points；保留首点；行数较小时不抽稀 |
| test_visibility_manager.py | 公共图例与局部曲线最后操作优先 |
| test_project_serialization.py | ProjectConfig to_dict/from_dict 往返一致 |
| test_data_manager.py | 别名递增、文件移除、列查询 |

### 15.2 可见性测试用例

场景 A：

```text
1. data1 全局显示 version=1
2. vx 图窗中 data1/vx 局部隐藏 version=2
结果：data1/vx 隐藏
```

场景 B：

```text
1. vx 图窗中 data1/vx 局部隐藏 version=2
2. data1 全局显示 version=3
结果：data1/vx 显示
```

场景 C：

```text
1. data1 全局隐藏 version=4
2. vx 图窗中 data1/vx 局部显示 version=5
结果：data1/vx 显示，但 data1 三维轨迹隐藏
```

### 15.3 手动验收清单

MVP 完成后，至少执行以下手动验收：

1. 打开一个样例 CSV，默认 9 图窗正常绘制。
2. 打开多个 CSV，底部公共图例显示 data1、data2、data3。
3. 修改别名后，公共图例与曲线标签刷新。
4. 修改文件颜色后，三维轨迹和默认图窗曲线颜色刷新。
5. 默认图窗设置按钮只显示绘图细节。
6. 默认图窗曲线按钮只允许显示/隐藏各文件曲线。
7. 自定义选项卡可以创建 2×3 布局。
8. 自定义图窗横向对比可以绘制所有 CSV 的同一列。
9. 自定义图窗纵向对比可以绘制同一 CSV 的多列。
10. 纵向对比切换文件时，能复用同名列。
11. 手动添加曲线功能可用。
12. 公共图例与局部曲线窗口的最后操作优先规则正确。
13. 保存工程 JSON 后关闭软件，再加载工程能恢复配置。
14. CSV 路径失效时能提示并允许重新定位或跳过。
15. 三维轨迹超过 50000 点时自动抽稀。
16. 单个二维图窗和三维轨迹能导出 PNG。

---

## 16. 开发阶段拆分

### 阶段 0：工程初始化

目标：搭建可运行空壳。

任务：

1. 创建目录结构。
2. 配置 requirements.txt 和 pyproject.toml。
3. 创建 main.py。
4. 创建 MainWindow 空窗口。
5. 创建基础菜单栏。
6. 确保 `python main.py` 能启动空窗口。

验收：

- 可启动主窗口；
- 无报错；
- 工程结构符合规划。

### 阶段 1：数据模型与 JSON 序列化

目标：完成核心 dataclass 模型。

任务：

1. 实现 DataFileConfig、DisplayConfig、PresetPlotConfig、CurveConfig、CustomPlotConfig、TabConfig、ProjectConfig。
2. 实现 to_dict/from_dict。
3. 实现默认工程创建函数。
4. 实现默认 3×3 TabConfig 创建函数。
5. 编写序列化单元测试。

验收：

- 默认工程可生成；
- 保存为 JSON 后可恢复；
- 默认 3×3 配置正确。

### 阶段 2：CSV 读取与列识别

目标：能读取 CSV 并识别关键列。

任务：

1. 实现 CsvLoader。
2. 实现 ColumnDetector。
3. 实现 DataManager。
4. 实现别名递增机制。
5. 加入行数和文件数限制。
6. 编写列识别测试。

验收：

- 能读取样例 CSV；
- 自动识别 time/x/y/z/vx/vy/vz/phi/theta/psi/wx/wy/wz；
- 别名为 data1、data2 等；
- 删除 data2 后再添加为 data4。

### 阶段 3：主界面布局

目标：完成主界面框架。

任务：

1. MainWindow 创建 QSplitter。
2. 左侧放 TrajectoryView。
3. 右侧放 QTabWidget。
4. 底部放 LegendBar。
5. 默认选项卡显示 3×3 PlotCell。
6. 每个图窗右下角有 `[曲线] [设置]` 两个按钮。

验收：

- 界面布局符合设计；
- 左右比例约 2/5 和 3/5；
- 底部公共图例区存在；
- 默认 9 个图窗出现。

### 阶段 4：Matplotlib 绘图嵌入

目标：默认图窗和三维轨迹能绘制数据。

任务：

1. 实现 MplCanvas。
2. 实现 PresetPlotCell 绘制。
3. 实现 TrajectoryView 绘制。
4. 实现 downsample。
5. 加入起点/终点标记。
6. 添加等比例坐标轴函数。

验收：

- 加载样例 CSV 后，三维轨迹显示；
- 默认 9 个图窗显示；
- 轨迹超过 50000 点时抽稀；
- 起点/终点标记可见。

### 阶段 5：导入、文件管理与公共图例

目标：多文件导入和公共图例可用。

任务：

1. 实现 ImportFilesDialog。
2. 实现 LegendBar 和 LegendItemWidget。
3. 实现颜色修改。
4. 实现别名修改。
5. 实现全局显示/隐藏。
6. 实现 FileManagerDialog 初版。

验收：

- 可一次选择多个 CSV；
- 加载时可修改别名；
- 公共图例显示所有文件；
- 修改颜色后曲线刷新；
- 全局隐藏文件后所有相关二维曲线和三维轨迹更新。

### 阶段 6：可见性最后操作优先

目标：实现全局与局部显示/隐藏优先级。

任务：

1. 实现 visibility_counter。
2. 实现 DataFileConfig visibility_version。
3. 实现 PresetPlotConfig.curve_visibility。
4. 实现 CurveConfig.visibility_version。
5. 实现 effective visibility 函数。
6. 编写单元测试。

验收：

- 全局隐藏后局部显示可以覆盖；
- 局部隐藏后全局显示可以覆盖；
- 三维轨迹仅受全局控制。

### 阶段 7：默认图窗设置与曲线窗口

目标：默认图窗交互完成。

任务：

1. 实现 PresetPlotSettingsDialog。
2. 实现默认图窗简化 CurveManagerDialog。
3. 支持标题、坐标标签、网格、图例、轴范围、线宽、线型设置。
4. 支持默认图窗中各文件曲线显示/隐藏。
5. 保存相关配置。

验收：

- 默认图窗不能添加曲线；
- 默认图窗不能切换绘图变量；
- 曲线按钮只用于显示/隐藏；
- 设置项能保存和恢复。

### 阶段 8：自定义选项卡与自定义图窗

目标：完成自定义页面与图窗。

任务：

1. 实现 NewTabDialog。
2. 实现 CustomPlotCell。
3. 实现 CustomPlotSettingsDialog 多选项卡。
4. 实现 CompareModeWidget。
5. 实现 DisplaySettingsWidget。
6. 实现 AddCurveWidget。
7. 实现完整 CurveManagerDialog。

验收：

- 可新建 1×1 到 5×5 自定义选项卡；
- 空白图窗允许存在；
- 可配置横向对比；
- 可配置纵向对比；
- 可手动添加曲线；
- 可删除、排序、修改自定义曲线样式。

### 阶段 9：工程保存、加载、自动保存

目标：工程配置完整持久化。

任务：

1. 实现 ProjectIO。
2. 实现 ProjectManager 保存/另存为/加载。
3. 实现自动保存 QTimer。
4. 实现路径失效处理。
5. 实现关闭窗口前保存提示。

验收：

- 保存 JSON 后可重新加载；
- 图窗配置、曲线显示状态、别名、颜色、列映射都能恢复；
- 路径失效时能重新定位或跳过；
- 自动保存不会频繁写文件。

### 阶段 10：导出与打包

目标：完成 MVP 交付。

任务：

1. 实现二维图窗导出 PNG。
2. 实现三维轨迹导出 PNG。
3. 编写 README 使用说明。
4. 编写 build_windows.bat。
5. 使用 PyInstaller 打包。
6. 在干净环境中运行打包程序。

验收：

- 可导出 PNG；
- 可双击运行；
- 打包程序能打开 CSV、保存工程、加载工程。

---

## 17. 智能体实现提示词模板

以下内容可以直接作为给 Codex 或其他代码智能体的执行提示。

### 17.1 总提示

```text
你正在实现一个 Python + PySide6 桌面软件，名称为 FlightCSVVisualizer。
请严格遵守《飞行器 CSV 数据可视化软件设计文档 v0.1》和《执行计划 v0.1》。第一版只实现 MVP，不要添加地图背景、实时数据流、复杂滤波、三维实体模型等额外功能。

技术栈：PySide6、pandas、numpy、matplotlib、json、dataclasses、pytest。

核心要求：
1. 主界面左侧为三维轨迹，右侧为选项卡二维图窗，底部为公共图例。
2. 默认选项卡为 3×3 预设图窗，固定显示 vx/vy/vz、phi/theta/psi、wx/wy/wz。
3. 默认图窗只允许修改绘图细节和当前图窗曲线显示/隐藏，不允许添加曲线或修改变量。
4. 自定义图窗支持横向对比、纵向对比、手动添加曲线。
5. 公共图例和单图窗曲线窗口的显示/隐藏采用“最后一次操作优先”，用 visibility_counter 实现。
6. 工程配置保存为 JSON，重要操作后 1 秒防抖自动保存。
7. 代码必须模块化，模型、核心逻辑、绘图、UI 分层实现。

请先完成当前阶段任务，不要跨阶段大改结构。每完成一个阶段，运行相关测试并说明验收结果。
```

### 17.2 阶段任务提示模板

```text
当前任务：实现阶段 N：<阶段名称>。

请完成以下内容：
1. <任务1>
2. <任务2>
3. <任务3>

约束：
- 不要改变已定义的数据结构，除非发现明显问题并说明原因。
- 不要实现下一阶段功能。
- 为非 UI 核心逻辑编写 pytest。
- 保证 python main.py 能启动。
- 修改后给出变更文件列表和测试结果。
```

### 17.3 可见性逻辑专项提示

```text
请实现公共图例与局部曲线显示/隐藏的“最后一次操作优先”机制。
不要使用简单的 global_visible && local_visible。

项目中有 ProjectConfig.visibility_counter，每次显示/隐藏操作递增。
DataFileConfig 保存 visible 和 visibility_version。
PresetPlotConfig.curve_visibility[file_id] 保存该预设图窗内文件曲线的局部 VisibilityState。
CurveConfig 保存自定义曲线的 visible 和 visibility_version。

有效可见性判断：
- 默认图窗：如果局部 visibility version 晚于文件全局 version，则使用局部 visible，否则使用文件 visible。
- 自定义图窗：如果曲线 visibility_version 晚于文件全局 version，则使用曲线 visible，否则使用文件 visible。
- 三维轨迹：只使用文件全局 visible。

请为该逻辑编写单元测试，覆盖全局覆盖局部、局部覆盖全局、无局部状态三类情况。
```

---

## 18. 编码规范建议

1. UI 层不要直接读写 CSV，必须通过 DataManager。
2. 绘图层不要直接弹窗，缺失列警告由调用者处理。
3. JSON 保存不保存 DataFrame，只保存路径、别名、颜色、列映射和图窗配置。
4. 函数尽量短小，每个函数只做一件事。
5. 数据模型字段名保持稳定，避免频繁改变 JSON 结构。
6. 所有 `file_id`、`plot_id`、`curve_id` 应使用稳定 ID，不要用列表下标。
7. 用户可见文本集中管理，后续方便国际化。
8. 不要在绘图函数中创建 UI 控件。
9. 不要在 UI 线程中执行耗时 CSV 读取，若文件较大应使用 worker。
10. 所有异常都应转成用户可理解的提示，不要让程序直接崩溃。

---

## 19. 常见风险与规避

| 风险 | 说明 | 规避方式 |
|---|---|---|
| 默认图窗和自定义图窗混淆 | 默认图窗不应开放完整配置 | 使用 plot_type 明确区分 preset/custom |
| 可见性逻辑写错 | 容易写成全局 && 局部 | 使用 visibility_counter，并写单元测试 |
| Matplotlib 画布过多导致卡顿 | 自定义 5×5 可能有很多图 | 第一版限制文件数和点数，必要时刷新当前页 |
| JSON 结构频繁变化 | 后续工程文件不兼容 | 定义 project_version，集中序列化 |
| CSV 路径失效 | 工程加载失败 | 支持重新定位或跳过 |
| 列名不统一 | 默认图窗缺列 | 使用 column_mapping 和缺列跳过策略 |
| 自动保存频繁写盘 | 连续修改配置 | QTimer 防抖，原子写入 |
| 用户误删曲线 | 自定义图窗删除曲线不可恢复 | 删除前确认，或提供撤销作为后续功能 |
| 打包后资源丢失 | 图标/QSS 找不到 | 使用统一 resource_path 工具函数 |

---

## 20. 第一版 MVP 验收标准

第一版完成后，应满足以下标准：

1. 软件可通过 `python main.py` 启动。
2. 软件可通过 PyInstaller 打包为可双击运行程序。
3. 可读取一个或多个 CSV 文件。
4. 加载 CSV 时可设置别名，默认 data1、data2 等，删除后编号不复用。
5. 可自动识别样例 CSV 中的 time、x/y/z、vx/vy/vz、phi/theta/psi、wx/wy/wz。
6. 自动识别失败时可手动列映射。
7. 左侧三维轨迹正常显示，最大显示点数为 50000，超过自动抽稀。
8. 右侧默认 3×3 图窗固定显示速度、姿态、角速度。
9. 默认图窗只允许绘图细节设置，不允许添加曲线。
10. 默认图窗曲线窗口只允许显示/隐藏该图窗内各文件曲线。
11. 底部公共图例可控制文件全局显示/隐藏、颜色和别名。
12. 公共图例与局部曲线窗口的显示/隐藏满足最后操作优先。
13. 可添加自定义选项卡，布局最大 5×5。
14. 自定义图窗支持横向对比、纵向对比和手动添加曲线。
15. 自定义图窗曲线管理窗口支持显示/隐藏、删除、排序和样式调整。
16. 工程 JSON 可保存和加载，恢复文件、别名、颜色、列映射、图窗配置和可见性状态。
17. CSV 路径失效时可重新定位或跳过。
18. 支持单个二维图窗导出 PNG。
19. 支持三维轨迹导出 PNG。
20. 关键非 UI 逻辑有 pytest 测试。

---

## 21. 第二阶段可扩展方向

第一版完成并稳定后，再考虑：

1. 单位转换：rad/deg、rad/s/deg/s。
2. 选项卡整体导出 PNG。
3. 批量导出所有图窗。
4. 数据滤波与平滑。
5. 时间对齐与插值。
6. 误差曲线和差值分析。
7. 轨迹动画播放。
8. 更高性能绘图后端，例如 PyQtGraph、VisPy 或 PyVista。
9. 经纬高/ENU/NED 坐标转换。
10. 工程模板和预设图窗模板。
11. 撤销/重做机制。
12. 图窗拖拽重排。

---

## 22. 建议的第一轮实际编码顺序

如果让智能体开始写代码，建议按以下顺序推进：

```text
1. 阶段 0：工程初始化
2. 阶段 1：数据模型与 JSON 序列化
3. 阶段 2：CSV 读取与列识别
4. 阶段 6：可见性最后操作优先逻辑
5. 阶段 3：主界面布局
6. 阶段 4：绘图嵌入
7. 阶段 5：导入窗口、文件管理、公共图例
8. 阶段 7：默认图窗设置与曲线窗口
9. 阶段 8：自定义图窗
10. 阶段 9：工程保存、加载、自动保存
11. 阶段 10：导出与打包
```

其中第 6 阶段的可见性逻辑虽然属于交互细节，但建议提前实现和测试，因为它会影响公共图例、默认图窗、自定义图窗和 JSON 结构。

---

## 23. 给开发智能体的最终边界说明

开发智能体在实现过程中必须遵守以下边界：

1. 不要改变默认 3×3 图窗的固定变量规则。
2. 不要给默认 3×3 图窗添加横向/纵向对比设置页。
3. 不要把公共图例逻辑写成绝对优先。
4. 不要把局部曲线逻辑写成绝对优先。
5. 不要使用简单的 `global_visible && local_visible`。
6. 不要把 DataFrame 写入 JSON。
7. 不要在第一版实现单位转换、地图背景、轨迹动画。
8. 不要让自定义选项卡超过 5×5。
9. 不要让 CSV 默认加载数量超过 10 个而无提示。
10. 不要忽略路径失效恢复逻辑。

只要严格按本执行计划推进，第一版软件应能形成一个可运行、可配置、可扩展的轻量级飞行器 CSV 数据可视化工具。
