"""Upload session management: create, upload, validate, preview."""

import logging
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from api.db.models import UploadSession
from api.models.ingest import (
    FilePreview,
    PreviewData,
    ValidationIssue,
    ValidationResult,
)
from api.services.audit_service import log_action

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB per file
MAX_TOTAL_SIZE = 200 * 1024 * 1024  # 200 MB total

REQUIRED_FILE_TYPES = {"applicants", "experiences"}
OPTIONAL_FILE_TYPES = {
    "personal_statement", "secondary_application", "gpa_trend",
    "language", "parents", "schools",
    "military", "siblings", "academic_records",
}


def create_session(db: Session, user_id: uuid.UUID, cycle_year: int) -> UploadSession:
    """Create a new upload session."""
    session = UploadSession(
        id=uuid.uuid4(),
        uploaded_by=user_id,
        cycle_year=cycle_year,
        status="uploaded",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def save_uploaded_files(
    upload_session: UploadSession,
    files: list[UploadFile],
) -> tuple[dict, list[str]]:
    """Save uploaded files to a temp directory and detect types.

    Returns (file_manifest, errors).
    In production this would upload to Azure Blob Storage.
    """
    from pipeline.file_detection import detect_file_type

    session_dir = Path(tempfile.gettempdir()) / "rmc_uploads" / str(upload_session.id)
    session_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict = {}
    errors: list[str] = []
    total_size = 0

    for f in files:
        if not f.filename:
            continue

        # Read file content
        content = f.file.read()
        size = len(content)

        if size > MAX_FILE_SIZE:
            errors.append(f"{f.filename}: exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit")
            continue

        total_size += size
        if total_size > MAX_TOTAL_SIZE:
            errors.append(f"Total upload size exceeds {MAX_TOTAL_SIZE // (1024*1024)}MB limit")
            break

        # Check extension
        if not f.filename.lower().endswith(".xlsx"):
            errors.append(f"{f.filename}: only .xlsx files are accepted")
            continue

        # Sanitize filename to prevent path traversal
        from pathlib import PurePosixPath
        safe_name = PurePosixPath(f.filename).name

        # Reject dotfiles and empty names
        if not safe_name or safe_name.startswith('.'):
            errors.append(f"{f.filename}: invalid filename")
            continue

        # Save to disk with sanitized name
        dest = session_dir / safe_name

        # Belt-and-suspenders: verify resolved path is within session_dir
        if not dest.resolve().is_relative_to(session_dir.resolve()):
            errors.append(f"{f.filename}: path traversal attempt detected")
            continue

        dest.write_bytes(content)

        # Detect type
        detected_type = detect_file_type(dest)

        # Use safe_name in manifest (sanitized filename)
        manifest[safe_name] = {
            "size": size,
            "local_path": str(dest),
            "detected_type": detected_type,
        }
        logger.info("Saved %s (%d bytes) -> %s", safe_name, size, detected_type)

    return manifest, errors


def validate_session(
    db: Session,
    upload_session: UploadSession,
) -> ValidationResult:
    """Validate an uploaded session's files."""
    import pandas as pd

    manifest = upload_session.file_manifest or {}
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    info: list[str] = []

    # Check required files
    detected_types = {v["detected_type"] for v in manifest.values() if v.get("detected_type")}

    for req in REQUIRED_FILE_TYPES:
        if req not in detected_types:
            errors.append(ValidationIssue(
                severity="error",
                file_type=req,
                message=f"Required file type '{req}' not detected in uploaded files",
            ))

    # Per-file validation
    applicant_count = 0
    for filename, meta in manifest.items():
        local_path = meta.get("local_path")
        if not local_path or not Path(local_path).exists():
            errors.append(ValidationIssue(
                severity="error",
                file_type=meta.get("detected_type"),
                message=f"File {filename} not found on disk",
            ))
            continue

        try:
            # Read once, reuse (eliminates duplicate file read)
            df_full = pd.read_excel(local_path, engine="openpyxl")
            row_count = len(df_full)
            df = df_full.head(5)
        except Exception as exc:
            errors.append(ValidationIssue(
                severity="error",
                file_type=meta.get("detected_type"),
                message=f"Cannot read {filename}: {exc}",
            ))
            continue

        if meta.get("detected_type") == "applicants":
            applicant_count = row_count
            # Check for required columns
            cols_lower = {c.lower().replace(" ", "_") for c in df.columns}
            if not any("amcas" in c for c in cols_lower):
                errors.append(ValidationIssue(
                    severity="error",
                    file_type="applicants",
                    message=f"Applicants file missing AMCAS ID column",
                    detail=f"Columns found: {list(df.columns)[:10]}",
                ))

        info.append(f"{filename}: {row_count} rows, type={meta.get('detected_type')}")

    if applicant_count > 0 and applicant_count < 100:
        warnings.append(ValidationIssue(
            severity="warning",
            file_type="applicants",
            message=f"Only {applicant_count} applicants found (expected 1000+)",
        ))

    info.append(f"Total applicants: {applicant_count}")

    result = ValidationResult(errors=errors, warnings=warnings, info=info)

    # Update session
    upload_session.validation_result = result.model_dump()
    if errors:
        upload_session.status = "uploaded"  # stay in uploaded if errors
    else:
        upload_session.status = "validated"
    db.commit()

    log_action(
        db,
        upload_session.uploaded_by,
        "validate",
        resource_type="upload_session",
        resource_id=str(upload_session.id),
        metadata={"error_count": len(errors), "warning_count": len(warnings)},
    )

    return result


def get_preview(
    _db: Session,
    upload_session: UploadSession,
) -> PreviewData:
    """Build a preview of the uploaded session's data."""
    import pandas as pd

    manifest = upload_session.file_manifest or {}
    file_previews: list[FilePreview] = []

    for filename, meta in manifest.items():
        local_path = meta.get("local_path")
        if not local_path or not Path(local_path).exists():
            continue

        try:
            df_full = pd.read_excel(local_path, engine="openpyxl")
            # Truncate text columns for PII safety
            sample = df_full.head(10).copy()
            for col in sample.select_dtypes(include=["object"]).columns:
                sample[col] = sample[col].astype(str).str[:100]

            file_previews.append(FilePreview(
                filename=filename,
                detected_type=meta.get("detected_type"),
                row_count=len(df_full),
                column_count=len(df_full.columns),
                columns=list(df_full.columns)[:50],
                sample_rows=sample.to_dict(orient="records"),
            ))
        except Exception:
            logger.warning("Could not preview %s", filename)

    validation = None
    if upload_session.validation_result:
        validation = ValidationResult(**upload_session.validation_result)

    return PreviewData(
        session_id=str(upload_session.id),
        cycle_year=upload_session.cycle_year,
        status=upload_session.status,
        files=file_previews,
        validation=validation,
    )
