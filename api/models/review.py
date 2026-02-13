"""Pydantic models for review queue and feedback."""

from pydantic import BaseModel


FLAG_REASONS = [
    "Undervalued volunteer/community work",
    "Undervalued clinical experience",
    "Missed grit/adversity indicators",
    "Overvalued — application weaker than score suggests",
    "Other",
]


class ReviewDecision(BaseModel):
    decision: str  # "confirm" or "flag"
    notes: str = ""
    flag_reason: str | None = None  # required when decision == "flag"


class ReviewQueueItem(BaseModel):
    amcas_id: int
    tier: int
    tier_label: str
    predicted_score: float
    confidence: float
    clf_reg_agree: bool
    priority_reason: str
    decision: str | None = None
    notes: str | None = None
    flag_reason: str | None = None
