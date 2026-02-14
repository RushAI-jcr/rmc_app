"""Review queue endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from api.db.models import User
from api.db.session import get_db
from api.dependencies import get_active_cycle_year, get_current_user, rate_limit
from api.models.review import ReviewDecision, ReviewQueueItem, FLAG_REASONS
from api.services.audit_service import log_action
from api.models.applicant import RubricScorecard
from api.services.review_service import get_review_queue, save_decision, get_flag_summary, get_progress

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/queue")
def review_queue(
    request: Request,
    config: str = "A_Structured",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    cycle_year: int = Depends(get_active_cycle_year),
) -> list[ReviewQueueItem]:
    """Get the prioritized review queue (Tier 2 + Tier 3 only)."""
    store = request.app.state.store
    queue = get_review_queue(config, store, db=db, cycle_year=cycle_year)
    log_action(db, current_user.id, "view_review_queue", resource_type="review")
    return [ReviewQueueItem(**item) for item in queue]


@router.get("/flag-reasons")
def flag_reasons(current_user: User = Depends(get_current_user)) -> list[str]:
    """Get the list of valid flag reasons."""
    return FLAG_REASONS


@router.get("/flag-summary")
def flag_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Get summary of flags for the current cycle."""
    log_action(db, current_user.id, "view_flag_summary", resource_type="review")
    return get_flag_summary()


@router.get("/queue/next")
def next_unreviewed(
    request: Request,
    config: str = "A_Structured",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    cycle_year: int = Depends(get_active_cycle_year),
) -> ReviewQueueItem | None:
    """Get the next unreviewed applicant in the queue."""
    store = request.app.state.store
    queue = get_review_queue(config, store, db=db, cycle_year=cycle_year)
    for item in queue:
        if item["decision"] is None:
            return ReviewQueueItem(**item)
    return None


@router.get("/progress")
def review_progress(
    request: Request,
    config: str = "A_Structured",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    cycle_year: int = Depends(get_active_cycle_year),
) -> dict:
    """Get review progress counts for the active cycle."""
    store = request.app.state.store
    queue = get_review_queue(config, store, db=db, cycle_year=cycle_year)
    return get_progress(db, cycle_year, total_in_queue=len(queue))


@router.get("/queue/{amcas_id}/detail")
def review_detail(
    request: Request,
    amcas_id: int,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Lightweight rubric scorecard for one applicant (no SHAP, no class probs)."""
    from api.routers.applicants import _build_rubric_scorecard

    store = request.app.state.store
    rubric_data = store.rubric_scores.get(str(amcas_id))
    scorecard = None
    if rubric_data:
        scorecard = _build_rubric_scorecard(rubric_data)
    return {"amcas_id": amcas_id, "rubric_scorecard": scorecard}


_decision_rate_limit = rate_limit("decision", max_requests=60, window_seconds=60)


@router.post("/{amcas_id}/decision")
def submit_decision(
    request: Request,
    amcas_id: int,
    body: ReviewDecision,
    current_user: User = Depends(_decision_rate_limit),
    db: Session = Depends(get_db),
    cycle_year: int = Depends(get_active_cycle_year),
) -> dict:
    """Save a review decision (confirm or flag) for an applicant."""
    store = request.app.state.store
    # Look up predicted score/tier for snapshot
    predictions = store.get_predictions("A_Structured")
    match = next((p for p in predictions if p["amcas_id"] == amcas_id), None)
    save_decision(
        db=db,
        amcas_id=amcas_id,
        user_id=current_user.id,
        cycle_year=cycle_year,
        decision=body.decision,
        notes=body.notes,
        predicted_score=match["predicted_score"] if match else None,
        predicted_tier=match["tier"] if match else None,
        flag_reason=body.flag_reason,
    )
    log_action(
        db, current_user.id, "submit_decision",
        resource_type="review", resource_id=str(amcas_id),
        metadata={"decision": body.decision, "flag_reason": body.flag_reason},
    )
    return {"status": "saved", "amcas_id": amcas_id, "decision": body.decision}
