"""Translate pipeline exceptions to user-friendly messages."""

import logging

logger = logging.getLogger(__name__)

_ERROR_MAP: list[tuple[type, str, str]] = [
    (KeyError, "Amcas_ID", "The Applicants file is missing the required 'AMCAS ID' column."),
    (FileNotFoundError, "", "A required data file was not found."),
    (MemoryError, "", "The uploaded files are too large to process. Please contact support."),
]


def translate_error(exc: Exception, step: str) -> str:
    """Map a pipeline exception to a user-friendly message."""
    exc_msg = str(exc)

    for err_type, pattern, friendly_msg in _ERROR_MAP:
        if isinstance(exc, err_type) and pattern in exc_msg:
            return friendly_msg

    return f"Pipeline error during {step}: {exc_msg[:200]}"
