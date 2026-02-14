"""Pipeline status and monitoring endpoints."""

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db.models import PipelineRun, User
from api.db.session import get_db
from api.dependencies import require_admin

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


class PipelineRunStatus(BaseModel):
    id: str
    upload_session_id: str
    status: str
    current_step: str | None = None
    progress_pct: int
    started_at: str | None = None
    completed_at: str | None = None
    result_summary: dict | None = None
    error_log: str | None = None


@router.get("/runs/{run_id}")
def get_run_status(
    run_id: str,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PipelineRunStatus:
    """Get the status of a pipeline run."""
    run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")

    return PipelineRunStatus(
        id=str(run.id),
        upload_session_id=str(run.upload_session_id),
        status=run.status,
        current_step=run.current_step,
        progress_pct=run.progress_pct,
        started_at=run.started_at.isoformat() if run.started_at else None,
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
        result_summary=run.result_summary,
        error_log=run.error_log if run.status == "failed" else None,
    )


@router.get("/runs")
def list_runs(
    session_id: str | None = None,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[PipelineRunStatus]:
    """List pipeline runs, optionally filtered by session."""
    query = db.query(PipelineRun).order_by(PipelineRun.updated_at.desc())
    if session_id:
        query = query.filter(PipelineRun.upload_session_id == session_id)
    runs = query.limit(50).all()

    return [
        PipelineRunStatus(
            id=str(r.id),
            upload_session_id=str(r.upload_session_id),
            status=r.status,
            current_step=r.current_step,
            progress_pct=r.progress_pct,
            started_at=r.started_at.isoformat() if r.started_at else None,
            completed_at=r.completed_at.isoformat() if r.completed_at else None,
            result_summary=r.result_summary,
            error_log=r.error_log if r.status == "failed" else None,
        )
        for r in runs
    ]
