"""Pydantic models for review queue and feedback."""

from typing import Literal

from pydantic import BaseModel, model_validator


FLAG_REASONS = [
    "Undervalued volunteer/community work",
    "Undervalued clinical experience",
    "Missed grit/adversity indicators",
    "Overvalued — application weaker than score suggests",
    "Other",
]


class ReviewDecision(BaseModel):
    decision: Literal["confirm", "flag"]
    notes: str = ""
    flag_reason: str | None = None

    @model_validator(mode="after")
    def validate_flag_fields(self) -> "ReviewDecision":
        if self.decision == "flag":
            if not self.flag_reason:
                raise ValueError("flag_reason is required when decision is 'flag'")
            if self.flag_reason not in FLAG_REASONS:
                raise ValueError(f"flag_reason must be one of: {FLAG_REASONS}")
            if self.flag_reason == "Other" and len(self.notes) < 10:
                raise ValueError("Notes must be at least 10 characters when flag_reason is 'Other'")
        return self


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
    reviewer_username: str | None = None
