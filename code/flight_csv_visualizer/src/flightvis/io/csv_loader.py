from __future__ import annotations

from pathlib import Path

import pandas as pd

from flightvis.constants import MAX_CSV_ROWS


class CsvLoadError(RuntimeError):
    pass


def read_csv(path: str | Path, max_rows: int = MAX_CSV_ROWS) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise CsvLoadError(f"CSV 文件不存在：{csv_path}")
    try:
        dataframe = pd.read_csv(csv_path)
    except Exception as exc:  # pragma: no cover - pandas exception detail varies
        raise CsvLoadError(f"读取 CSV 失败：{csv_path}\n{exc}") from exc
    if len(dataframe) > max_rows:
        raise CsvLoadError(f"CSV 有 {len(dataframe)} 行，超过上限 {max_rows} 行。")
    return dataframe
