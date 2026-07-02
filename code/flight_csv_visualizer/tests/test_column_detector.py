from flightvis.io.column_detector import detect_column_mapping


def test_detects_sample_columns():
    columns = [
        "time",
        "x",
        "y",
        "z",
        "vx",
        "vy",
        "vz",
        "phi",
        "theta",
        "psi",
        "wx",
        "wy",
        "wz",
    ]
    mapping = detect_column_mapping(columns)
    assert mapping["time"] == "time"
    assert mapping["x"] == "x"
    assert mapping["roll"] == "phi"
    assert mapping["pitch"] == "theta"
    assert mapping["yaw"] == "psi"
    assert mapping["wx"] == "wx"


def test_detects_case_and_separator_variants():
    mapping = detect_column_mapping(["Time", "position_x", "Velocity-Y", "ang_vel_z"])
    assert mapping["time"] == "Time"
    assert mapping["x"] == "position_x"
    assert mapping["vy"] == "Velocity-Y"
    assert mapping["wz"] == "ang_vel_z"
