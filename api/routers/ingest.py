"""Ingest endpoints: upload, validate, preview, approve, retry."""

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.db.models import PipelineRun, UploadSession, User
from api.db.session import get_db
from api.dependencies import get_current_user
from api.models.ingest import (
    PipelineRunResponse,
    PreviewData,
    SessionSummary,
    UploadResponse,
    ValidationResult,
)
from api.services.audit_service import log_action
from api.services.upload_service import (
    create_session,
    get_preview,
    save_uploaded_files,
    validate_session,
)

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


def verify_session_ownership(session: UploadSession, user: User) -> None:
    """Verify user owns the session or is admin.

    Raises HTTPException(403) if user doesn't have access.
    """
    if session.uploaded_by != user.id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )


@router.post("/upload")
def upload_files(
    cycle_year: int = Form(...),
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UploadResponse:
    """Upload xlsx files for a new admissions cycle."""
    session = create_session(db, user.id, cycle_year)

    manifest, errors = save_uploaded_files(session, files)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Upload validation failed", "errors": errors},
        )

    session.file_manifest = manifest
    db.commit()

    detected_types = {
        fname: meta.get("detected_type", "unknown")
        for fname, meta in manifest.items()
    }

    log_action(
        db, user.id, "upload",
        resource_type="upload_session",
        resource_id=str(session.id),
        metadata={"file_count": len(manifest), "cycle_year": cycle_year},
    )

    return UploadResponse(
        session_id=str(session.id),
        cycle_year=cycle_year,
        files_received=len(manifest),
        detected_types=detected_types,
        status=session.status,
    )


@router.get("/sessions")
def list_sessions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SessionSummary]:
    """List past upload sessions, most recent first."""
    sessions = (
        db.query(UploadSession)
        .order_by(UploadSession.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        SessionSummary(
            id=str(s.id),
            cycle_year=s.cycle_year,
            status=s.status,
            created_at=s.created_at,
            uploaded_by=s.uploaded_by.hex if s.uploaded_by else None,
        )
        for s in sessions
    ]


@router.get("/{session_id}/preview")
def preview_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PreviewData:
    """Get preview data for a session. Triggers validation if not yet run."""
    session = db.query(UploadSession).filter(UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    verify_session_ownership(session, user)

    # Auto-validate if not yet done
    if session.status == "uploaded" and not session.validation_result:
        validate_session(db, session)

    return get_preview(db, session)


@router.get("/{session_id}/validation")
def get_validation(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ValidationResult:
    """Get or run validation for a session."""
    session = db.query(UploadSession).filter(UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    verify_session_ownership(session, user)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.validation_result:
        return validate_session(db, session)

    return ValidationResult(**session.validation_result)


@router.post("/{session_id}/approve")
def approve_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PipelineRunResponse:
    """Approve session and enqueue pipeline run.

    Uses SELECT ... FOR UPDATE to prevent race conditions.
    """
    session = (
        db.query(UploadSession)
        .filter(UploadSession.id == session_id)
        .with_for_update()
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    verify_session_ownership(session, user)

    if session.status not in ("validated", "uploaded"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Session status is '{session.status}', cannot approve",
        )

    # Check validation passed
    if session.validation_result:
        vr = session.validation_result
        if vr.get("errors"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot approve: validation errors exist",
            )

    # Check no active pipeline run (enforced by partial unique index too)
    active_run = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.upload_session_id == session.id,
            PipelineRun.status.in_(["pending", "running"]),
        )
        .first()
    )
    if active_run:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pipeline run is already active for this session",
        )

    run = PipelineRun(
        id=uuid.uuid4(),
        upload_session_id=session.id,
        status="pending",
    )
    db.add(run)
    session.status = "approved"
    db.commit()

    # Enqueue Celery task (imported here to avoid circular imports)
    from api.tasks.pipeline_task import run_pipeline_task

    run_pipeline_task.delay(str(run.id))

    log_action(
        db, user.id, "approve",
        resource_type="upload_session",
        resource_id=str(session.id),
    )

    return PipelineRunResponse(run_id=str(run.id), status="pending")


@router.post("/{session_id}/retry")
def retry_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PipelineRunResponse:
    """Retry a failed session's pipeline."""
    session = (
        db.query(UploadSession)
        .filter(UploadSession.id == session_id)
        .with_for_update()
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    verify_session_ownership(session, user)

    if session.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Can only retry failed sessions (current: '{session.status}')",
        )

    run = PipelineRun(
        id=uuid.uuid4(),
        upload_session_id=session.id,
        status="pending",
    )
    db.add(run)
    session.status = "approved"
    db.commit()

    from api.tasks.pipeline_task import run_pipeline_task

    run_pipeline_task.delay(str(run.id))

    log_action(
        db, user.id, "retry",
        resource_type="upload_session",
        resource_id=str(session.id),
    )

    return PipelineRunResponse(run_id=str(run.id), status="pending")


@router.patch("/{session_id}/file-types")
def override_file_types(
    session_id: str,
    overrides: dict[str, str],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UploadResponse:
    """Manually override detected file types, then re-validate."""
    session = db.query(UploadSession).filter(UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    verify_session_ownership(session, user)

    manifest = session.file_manifest or {}
    for filename, new_type in overrides.items():
        if filename in manifest:
            manifest[filename]["detected_type"] = new_type

    session.file_manifest = manifest
    db.commit()

    # Re-validate
    validate_session(db, session)

    detected_types = {
        fname: meta.get("detected_type", "unknown")
        for fname, meta in manifest.items()
    }

    return UploadResponse(
        session_id=str(session.id),
        cycle_year=session.cycle_year,
        files_received=len(manifest),
        detected_types=detected_types,
        status=session.status,
    )
