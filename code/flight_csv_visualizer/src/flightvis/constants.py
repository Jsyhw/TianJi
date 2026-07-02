APP_NAME = "FlightCSVVisualizer"
PROJECT_VERSION = "0.1"
MAX_CSV_FILES = 10
MAX_CSV_ROWS = 100_000
TRAJECTORY_MAX_POINTS = 50_000

STANDARD_MAPPING_KEYS = [
    "time",
    "x",
    "y",
    "z",
    "vx",
    "vy",
    "vz",
    "roll",
    "pitch",
    "yaw",
    "wx",
    "wy",
    "wz",
]

DEFAULT_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

PRESET_PLOTS = [
    ("vx", "X方向速度", "vx"),
    ("vy", "Y方向速度", "vy"),
    ("vz", "Z方向速度", "vz"),
    ("roll", "滚转角", "phi / rad"),
    ("pitch", "俯仰角", "theta / rad"),
    ("yaw", "偏航角", "psi / rad"),
    ("wx", "X轴角速度", "wx / rad/s"),
    ("wy", "Y轴角速度", "wy / rad/s"),
    ("wz", "Z轴角速度", "wz / rad/s"),
]

LINE_STYLES = ["-", "--", "-.", ":"]
