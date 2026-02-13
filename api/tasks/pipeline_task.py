"""Celery task for running the score-only pipeline."""

import logging
import traceback
from datetime import datetime, timezone
from pathlib import Path

from api.celery_app import celery
from api.db.models import PipelineRun, UploadSession
from api.db.session import SessionLocal
from api.services.audit_service import log_action
from api.services.error_translation import translate_error

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=0)
def run_pipeline_task(self, run_id: str) -> dict:
    """Execute the score-only pipeline for a given PipelineRun.

    Updates PipelineRun progress in the database as each step completes.
    """
    db = SessionLocal()
    try:
        run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        if not run:
            logger.error("PipelineRun %s not found", run_id)
            return {"error": "Run not found"}

        session = db.query(UploadSession).filter(
            UploadSession.id == run.upload_session_id
        ).first()
        if not session:
            logger.error("UploadSession not found for run %s", run_id)
            return {"error": "Session not found"}

        # Mark as running
        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        session.status = "processing"
        db.commit()

        # Build file_map from manifest
        manifest = session.file_manifest or {}
        file_map: dict[str, Path] = {}
        data_dir = None

        for _filename, meta in manifest.items():
            local_path = meta.get("local_path")
            detected_type = meta.get("detected_type")
            if local_path and detected_type:
                file_map[detected_type] = Path(local_path)
                if data_dir is None:
                    data_dir = Path(local_path).parent

        if not data_dir:
            raise ValueError("No uploaded files found in session manifest")

        def progress_callback(step: str, pct: int) -> None:
            """Update pipeline run progress in DB."""
            run.current_step = step
            run.progress_pct = pct
            run.updated_at = datetime.now(timezone.utc)
            db.commit()

        # Run the pipeline
        from pipeline.score_pipeline import score_new_cycle

        result = score_new_cycle(
            data_dir=data_dir,
            cycle_year=session.cycle_year,
            file_map=file_map,
            progress_callback=progress_callback,
        )

        # Mark complete
        run.status = "complete"
        run.progress_pct = 100
        run.completed_at = datetime.now(timezone.utc)
        run.result_summary = result
        session.status = "complete"
        db.commit()

        log_action(
            db,
            session.uploaded_by,
            "pipeline_complete",
            resource_type="pipeline_run",
            resource_id=str(run.id),
            metadata=result,
        )

        logger.info("Pipeline run %s completed: %d applicants", run_id, result["applicant_count"])
        return result

    except Exception as exc:
        logger.exception("Pipeline run %s failed", run_id)

        # Update run as failed
        try:
            run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if run:
                run.status = "failed"
                run.error_log = traceback.format_exc()
                run.completed_at = datetime.now(timezone.utc)

                session = db.query(UploadSession).filter(
                    UploadSession.id == run.upload_session_id
                ).first()
                if session:
                    session.status = "failed"

                    # Translate error for user
                    step = run.current_step or "unknown"
                    friendly_msg = translate_error(exc, step)
                    run.result_summary = {"error": friendly_msg}

                    log_action(
                        db,
                        session.uploaded_by,
                        "pipeline_failed",
                        resource_type="pipeline_run",
                        resource_id=str(run.id),
                        metadata={"error": friendly_msg},
                    )

                db.commit()
        except Exception:
            logger.exception("Failed to update run status after error")

        return {"error": str(exc)}

    finally:
        db.close()
