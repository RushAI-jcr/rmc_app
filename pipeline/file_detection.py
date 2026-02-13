"""Detect AMCAS file types from xlsx column headers.

Three-layer strategy (simplest first):
  1. Exact filename match against known AMCAS export names
  2. Column-header heuristics (signature columns)
  3. Manual override via API
"""

import logging
from pathlib import Path

import pandas as pd

from pipeline.config import FILE_MAP

logger = logging.getLogger(__name__)

# Reverse map: filename -> logical type
_FILENAME_TO_TYPE: dict[str, str] = {}
for logical_name, fname in FILE_MAP.items():
    _FILENAME_TO_TYPE[fname.lower()] = logical_name

# Column signatures: if a file contains ALL of these columns, it's this type.
# Checked in order -- first match wins.
_COLUMN_SIGNATURES: list[tuple[str, list[str]]] = [
    ("applicants", ["application_review_score"]),
    ("experiences", ["exp_type"]),
    ("gpa_trend", ["total_gpa_trend"]),
    ("language", ["language_desc"]),
    ("parents", ["edu_level"]),
    ("personal_statement", ["personal_statement"]),
    ("secondary_application", ["1_-_personal_attributes"]),
    ("schools_2024", ["school_name"]),
    ("military", ["military_service_status"]),
    ("siblings", ["sibling"]),
    ("academic_records", ["gpa"]),
]


def _normalize_col(col: str) -> str:
    """Lowercase, strip, replace spaces with underscores."""
    return col.strip().replace(" ", "_").lower()


def detect_file_type(filepath: Path) -> str | None:
    """Detect logical file type from an xlsx file.

    Returns the logical name (e.g. 'applicants', 'experiences') or None.
    """
    # Layer 1: exact filename match
    fname_lower = filepath.name.lower()
    if fname_lower in _FILENAME_TO_TYPE:
        match = _FILENAME_TO_TYPE[fname_lower]
        logger.info("File %s matched by filename -> %s", filepath.name, match)
        return match

    # Layer 2: column header heuristics
    try:
        df = pd.read_excel(filepath, engine="openpyxl", nrows=0)
    except Exception:
        logger.warning("Could not read headers from %s", filepath.name)
        return None

    cols_normalized = {_normalize_col(c) for c in df.columns}

    for logical_type, signature_cols in _COLUMN_SIGNATURES:
        if all(_normalize_col(sc) in cols_normalized for sc in signature_cols):
            logger.info("File %s matched by columns -> %s", filepath.name, logical_type)
            return logical_type

    logger.warning("Could not detect type for %s", filepath.name)
    return None


def detect_all_files(
    filepaths: list[Path],
) -> tuple[dict[str, Path], list[Path]]:
    """Map logical file types to paths. Returns (detected, unrecognized)."""
    detected: dict[str, Path] = {}
    unrecognized: list[Path] = []

    for fp in filepaths:
        file_type = detect_file_type(fp)
        if file_type:
            detected[file_type] = fp
        else:
            unrecognized.append(fp)

    logger.info(
        "Detected %d/%d files: %s",
        len(detected), len(filepaths), list(detected.keys()),
    )
    if unrecognized:
        logger.warning(
            "Unrecognized files: %s",
            [f.name for f in unrecognized],
        )

    return detected, unrecognized
