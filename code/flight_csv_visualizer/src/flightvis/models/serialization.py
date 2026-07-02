from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any


def clean_dict(value: Any) -> Any:
    if is_dataclass(value):
        return clean_dict(asdict(value))
    if isinstance(value, dict):
        return {key: clean_dict(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_dict(item) for item in value]
    if isinstance(value, tuple):
        return [clean_dict(item) for item in value]
    return value


def optional_float_range(value: Any) -> tuple[float, float] | None:
    if value is None:
        return None
    if len(value) != 2:
        raise ValueError("Range must contain exactly two numbers")
    return (float(value[0]), float(value[1]))
