"""Pydantic models for triage operations."""

from pydantic import BaseModel


class TriageSummary(BaseModel):
    total_applicants: int
    tier_counts: dict[str, int]
    avg_confidence: float
    agreement_rate: float
    config_name: str


class TriageRunRequest(BaseModel):
    config_name: str = "A_Structured"


class TriageRunResponse(BaseModel):
    status: str
    total_processed: int
    tier_distribution: dict[str, int]
