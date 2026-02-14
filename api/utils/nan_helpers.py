"""NaN-safe type conversion helpers for pandas row data."""

import math


def safe_float(val: object, default: float = 0.0) -> float:
    """Convert a value to float, returning default for NaN/None."""
    if val is None:
        return default
    try:
        f = float(val)
        return default if math.isnan(f) else f
    except (TypeError, ValueError):
        return default


def safe_int(val: object, default: int = 0) -> int:
    """Convert a value to int, returning default for NaN/None."""
    f = safe_float(val, float("nan"))
    return default if math.isnan(f) else int(f)


def safe_str(val: object) -> str | None:
    """Convert a value to str, returning None for NaN/empty."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).strip()
    return s if s else None


def safe_bool(val: object) -> bool:
    """Convert a value to bool, treating 1/Yes/True as True."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return False
    if isinstance(val, (bool, int)):
        return bool(val)
    return str(val).strip().lower() in ("1", "yes", "true", "y")
