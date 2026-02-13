"""Review queue endpoints."""

from fastapi import APIRouter, Request

from api.models.review import ReviewDecision, ReviewQueueItem, FLAG_REASONS
from api.services.review_service import get_review_queue, save_decision, get_flag_summary

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/queue")
def review_queue(
    request: Request,
    config: str = "A_Structured",
    cycle_year: int | None = None,
) -> list[ReviewQueueItem]:
    """Get the prioritized review queue (Tier 2 + Tier 3 only)."""
    store = request.app.state.store
    queue = get_review_queue(config, store, cycle_year=cycle_year)
    return [ReviewQueueItem(**item) for item in queue]


@router.get("/flag-reasons")
def flag_reasons() -> list[str]:
    """Get the list of valid flag reasons."""
    return FLAG_REASONS


@router.get("/flag-summary")
def flag_summary() -> dict:
    """Get summary of flags for the current cycle."""
    return get_flag_summary()


@router.post("/{amcas_id}/decision")
def submit_decision(request: Request, amcas_id: int, body: ReviewDecision) -> dict:
    """Save a review decision (confirm or flag) for an applicant."""
    store = request.app.state.store
    save_decision(amcas_id, body.decision, body.notes, store, body.flag_reason)
    return {"status": "saved", "amcas_id": amcas_id, "decision": body.decision}
