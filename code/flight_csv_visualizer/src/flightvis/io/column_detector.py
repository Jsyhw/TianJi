from __future__ import annotations

from flightvis.constants import STANDARD_MAPPING_KEYS


CANDIDATES: dict[str, list[str]] = {
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


def normalize_name(value: str) -> str:
    return value.strip().replace("_", "").replace("-", "").lower()


def detect_column_mapping(columns: list[str]) -> dict[str, str | None]:
    mapping: dict[str, str | None] = {key: None for key in STANDARD_MAPPING_KEYS}
    exact_lookup = {column: column for column in columns}
    lower_lookup = {column.lower(): column for column in columns}
    normalized_lookup = {normalize_name(column): column for column in columns}

    for key, candidates in CANDIDATES.items():
        found = None
        for candidate in candidates:
            if candidate in exact_lookup:
                found = exact_lookup[candidate]
                break
        if found is None:
            for candidate in candidates:
                if candidate.lower() in lower_lookup:
                    found = lower_lookup[candidate.lower()]
                    break
        if found is None:
            for candidate in candidates:
                normalized = normalize_name(candidate)
                if normalized in normalized_lookup:
                    found = normalized_lookup[normalized]
                    break
        mapping[key] = found
    return mapping


def missing_required_mapping(mapping: dict[str, str | None]) -> list[str]:
    required = ["time", "x", "y", "z", "vx", "vy", "vz", "roll", "pitch", "yaw", "wx", "wy", "wz"]
    return [key for key in required if not mapping.get(key)]
