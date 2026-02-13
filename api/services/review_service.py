"""Review service: queue management, flag persistence, feedback loop."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from api.config import PROCESSED_DIR
from api.services.data_service import DataStore
from api.services.prediction_service import build_prediction_table

logger = logging.getLogger(__name__)

DECISIONS_FILE = PROCESSED_DIR / "review_decisions.json"
FLAGS_FILE = PROCESSED_DIR / "flags_current_cycle.json"


def get_review_queue(config_name: str, store: DataStore) -> list[dict]:
    """Get review queue filtered to Tier 2 + Tier 3 only.

    Human reviewers should never see Tier 0 or Tier 1 applicants.
    Queue is sorted by: disagreements first, then low confidence.
    """
    predictions = build_prediction_table(config_name, store)
    if not predictions:
        return []

    queue = []
    for p in predictions:
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

        decision_data = store.decisions.get(p["amcas_id"], {})

        item = {
            "amcas_id": p["amcas_id"],
            "tier": p["tier"],
            "tier_label": p["tier_label"],
            "predicted_score": p["predicted_score"],
            "confidence": p["confidence"],
            "clf_reg_agree": p["clf_reg_agree"],
            "priority_reason": reason,
            "decision": decision_data.get("decision"),
            "notes": decision_data.get("notes"),
            "flag_reason": decision_data.get("flag_reason"),
        }
        queue.append(item)

    # Sort: disagreements first, then by confidence ascending
    queue.sort(key=lambda x: (x["clf_reg_agree"], x["confidence"]))
    return queue


def save_decision(
    amcas_id: int,
    decision: str,
    notes: str,
    store: DataStore,
    flag_reason: str | None = None,
) -> None:
    """Save a review decision (confirm or flag)."""
    entry = {
        "decision": decision,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if decision == "flag" and flag_reason:
        entry["flag_reason"] = flag_reason

    store.decisions[amcas_id] = entry
    _persist_decisions(store)

    if decision == "flag":
        _append_flag(amcas_id, flag_reason or "", notes)
        logger.info("Flagged applicant %d: %s", amcas_id, flag_reason)
    else:
        logger.info("Confirmed score for applicant %d", amcas_id)


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


def _persist_decisions(store: DataStore) -> None:
    """Write decisions to disk."""
    serializable = {str(k): v for k, v in store.decisions.items()}
    with open(DECISIONS_FILE, "w") as f:
        json.dump(serializable, f, indent=2)


def load_decisions(store: DataStore) -> None:
    """Load decisions from disk at startup."""
    if DECISIONS_FILE.exists():
        with open(DECISIONS_FILE) as f:
            data = json.load(f)
        store.decisions = {int(k): v for k, v in data.items()}
        logger.info("Loaded %d review decisions", len(store.decisions))
