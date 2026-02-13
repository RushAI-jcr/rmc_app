"""Pydantic models for applicant data."""

from pydantic import BaseModel


class ApplicantSummary(BaseModel):
    amcas_id: int
    rank: int | None = None
    tier: int
    tier_label: str
    tier_color: str
    predicted_score: float
    predicted_bucket: int
    confidence: float
    clf_reg_agree: bool
    app_year: int | None = None


class RubricDimension(BaseModel):
    name: str
    score: float
    max_score: float = 5.0


class RubricGroup(BaseModel):
    label: str
    dimensions: list[RubricDimension]


class RubricScorecard(BaseModel):
    """Reviewer-facing rubric grouped by priority areas."""
    groups: list[RubricGroup]
    has_rubric: bool = False


# Keep old format for backward compatibility if needed
class RubricScores(BaseModel):
    personal_statement: dict[str, float] = {}
    experience_quality: dict[str, float] = {}
    secondary_essays: dict[str, float] = {}


class ShapDriver(BaseModel):
    feature: str
    display_name: str
    value: float
    direction: str  # "positive" or "negative"


class ApplicantDetail(BaseModel):
    amcas_id: int
    tier: int
    tier_label: str
    tier_color: str
    predicted_score: float
    predicted_bucket: int
    confidence: float
    clf_reg_agree: bool
    actual_score: float | None = None
    actual_bucket: int | None = None
    class_probabilities: list[float] = []
    shap_drivers: list[ShapDriver] = []
    rubric_scorecard: RubricScorecard | None = None
    app_year: int | None = None
    flag: "FlagInfo | None" = None


class FlagInfo(BaseModel):
    reason: str
    notes: str = ""
    flagged_at: str | None = None
