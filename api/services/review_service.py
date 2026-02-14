"""Review service: queue management, flag persistence, feedback loop."""

import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from api.config import PROCESSED_DIR
from api.db.models import ReviewDecision as ReviewDecisionModel
from api.services.data_service import DataStore

logger = logging.getLogger(__name__)

FLAGS_FILE = PROCESSED_DIR / "flags_current_cycle.json"


def get_review_queue(
    config_name: str,
    store: DataStore,
    db: Session,
    cycle_year: int,
) -> list[dict]:
    """Get review queue filtered to Tier 2 + Tier 3 only.

    Human reviewers should never see Tier 0 or Tier 1 applicants.
    Queue is sorted by: disagreements first, then low confidence.
    Decisions fetched in a single batch query (C6).
    """
    predictions = store.get_predictions(config_name)
    if not predictions:
        return []

    # Batch fetch all decisions for this cycle
    decisions = (
        db.query(ReviewDecisionModel)
        .filter(ReviewDecisionModel.cycle_year == cycle_year)
        .all()
    )
    decision_map = {d.amcas_id: d for d in decisions}

    queue = []
    for p in predictions:
        # Filter by cycle year
        if p.get("app_year") != cycle_year:
            continue
        # Only Tier 2 (Strong Candidate) and Tier 3 (Priority Interview)
        if p["tier"] < 2:
            continue

        reason = ""
        if not p["clf_reg_agree"]:
            reason = "Classifier/Regressor disagreement"
        elif p["confidence"] < 0.5:
            reason = "Low confidence"
        else:
            reason = "Standard review"

        decision_obj = decision_map.get(p["amcas_id"])

        item = {
            "amcas_id": p["amcas_id"],
            "tier": p["tier"],
            "tier_label": p["tier_label"],
            "predicted_score": p["predicted_score"],
            "confidence": p["confidence"],
            "clf_reg_agree": p["clf_reg_agree"],
            "priority_reason": reason,
            "decision": decision_obj.decision if decision_obj else None,
            "notes": decision_obj.notes if decision_obj else None,
            "flag_reason": decision_obj.flag_reason if decision_obj else None,
        }
        queue.append(item)

    # Sort: disagreements first, then by confidence ascending
    queue.sort(key=lambda x: (x["clf_reg_agree"], x["confidence"]))
    return queue


def save_decision(
    db: Session,
    amcas_id: int,
    user_id: UUID,
    cycle_year: int,
    decision: str,
    notes: str,
    predicted_score: float | None = None,
    predicted_tier: int | None = None,
    flag_reason: str | None = None,
) -> None:
    """Save a review decision using PostgreSQL upsert."""
    stmt = pg_insert(ReviewDecisionModel).values(
        amcas_id=amcas_id,
        reviewer_id=user_id,
        cycle_year=cycle_year,
        decision=decision,
        flag_reason=flag_reason,
        notes=notes,
        predicted_score=predicted_score,
        predicted_tier=predicted_tier,
    ).on_conflict_do_update(
        constraint="uq_review_decisions_applicant_cycle",
        set_={
            "decision": decision,
            "flag_reason": flag_reason,
            "notes": notes,
            "reviewer_id": user_id,
            "predicted_score": predicted_score,
            "predicted_tier": predicted_tier,
            "updated_at": func.now(),
        },
    )
    db.execute(stmt)
    db.commit()

    if decision == "flag":
        _append_flag(amcas_id, flag_reason or "", notes)
        logger.info("Flagged applicant %d: %s", amcas_id, flag_reason)
    else:
        logger.info("Confirmed score for applicant %d", amcas_id)


def get_decision_for_applicant(db: Session, amcas_id: int, cycle_year: int) -> ReviewDecisionModel | None:
    """Get the decision for a specific applicant in a cycle."""
    return (
        db.query(ReviewDecisionModel)
        .filter(
            ReviewDecisionModel.amcas_id == amcas_id,
            ReviewDecisionModel.cycle_year == cycle_year,
        )
        .first()
    )


def _append_flag(amcas_id: int, reason: str, notes: str) -> None:
    """Append flag to the per-cycle flags file for annual retrain."""
    flags = []
    if FLAGS_FILE.exists():
        with open(FLAGS_FILE) as f:
            flags = json.load(f)

    flags.append({
        "amcas_id": amcas_id,
        "flag_reason": reason,
        "notes": notes,
        "flagged_at": datetime.now(timezone.utc).isoformat(),
    })

    with open(FLAGS_FILE, "w") as f:
        json.dump(flags, f, indent=2)


def get_flag_summary() -> dict:
    """Get summary of flags for the current cycle."""
    if not FLAGS_FILE.exists():
        return {"total_flags": 0, "by_reason": {}}

    with open(FLAGS_FILE) as f:
        flags = json.load(f)

    by_reason: dict[str, int] = {}
    for flag in flags:
        reason = flag.get("flag_reason", "Unknown")
        by_reason[reason] = by_reason.get(reason, 0) + 1

    return {"total_flags": len(flags), "by_reason": by_reason}
