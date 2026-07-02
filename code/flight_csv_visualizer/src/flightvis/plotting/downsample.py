from __future__ import annotations

from math import ceil
from typing import Sequence, TypeVar

T = TypeVar("T")


def downsample_sequence(values: Sequence[T], max_points: int) -> Sequence[T]:
    if len(values) <= max_points:
        return values
    step = ceil(len(values) / max_points)
    return values[::step]


def downsample_xyz(x, y, z, max_points: int):
    if len(x) <= max_points:
        return x, y, z
    step = ceil(len(x) / max_points)
    return x[::step], y[::step], z[::step]
