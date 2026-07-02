from pathlib import Path


def app_data_dir() -> Path:
    path = Path.home() / ".flight_csv_visualizer"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_autosave_path() -> Path:
    return app_data_dir() / "autosave.flightvis.json"
