"""Triage service: tier assignment and pipeline stats."""

import logging

from api.config import TIER_LABELS, TIER_COLORS, score_to_tier
from api.services.data_service import DataStore

logger = logging.getLogger(__name__)


def run_triage(config_name: str, store: DataStore) -> dict:
    """Run triage on the test set and return summary."""
    predictions = store.get_predictions(config_name)
    if not predictions:
        return {"status": "error", "total_processed": 0, "tier_distribution": {}}

    tier_counts = {}
    for label in TIER_LABELS:
        tier_counts[label] = sum(1 for p in predictions if p["tier_label"] == label)

    return {
        "status": "success",
        "total_processed": len(predictions),
        "tier_distribution": tier_counts,
    }


def get_triage_summary(config_name: str, store: DataStore) -> dict:
    """Get triage summary stats."""
    predictions = store.get_predictions(config_name)
    if not predictions:
        return {
            "total_applicants": 0,
            "tier_counts": {},
            "avg_confidence": 0.0,
            "agreement_rate": 0.0,
            "config_name": config_name,
        }

    tier_counts = {}
    for label in TIER_LABELS:
        tier_counts[label] = sum(1 for p in predictions if p["tier_label"] == label)

    avg_confidence = sum(p["confidence"] for p in predictions) / len(predictions)
    agreement_rate = sum(1 for p in predictions if p["clf_reg_agree"]) / len(predictions)

    return {
        "total_applicants": len(predictions),
        "tier_counts": tier_counts,
        "avg_confidence": round(avg_confidence, 3),
        "agreement_rate": round(agreement_rate, 3),
        "config_name": config_name,
    }
