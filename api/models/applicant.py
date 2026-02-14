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


class RubricDimensionDetail(BaseModel):
    evidence_extracted: str = ""
    reasoning: str = ""


class RubricDimension(BaseModel):
    name: str
    score: float
    max_score: float = 4.0
    detail: RubricDimensionDetail | None = None


class RubricGroup(BaseModel):
    label: str
    dimensions: list[RubricDimension]


class RubricScorecard(BaseModel):
    """Reviewer-facing rubric grouped by priority areas."""
    groups: list[RubricGroup]
    has_rubric: bool = False


class ShapDriver(BaseModel):
    feature: str
    display_name: str
    value: float
    direction: str  # "positive" or "negative"


class ApplicantProfile(BaseModel):
    """Biographical & demographic data from AMCAS."""
    age: int | None = None
    gender: str | None = None
    citizenship: str | None = None
    ses_value: int | None = None
    first_generation: bool = False
    disadvantaged: bool = False
    pell_grant: bool = False
    fee_assistance: bool = False
    military_service: bool = False
    childhood_med_underserved: bool = False
    paid_employment_bf_18: bool = False
    contribution_to_family: bool = False
    employed_undergrad: bool = False
    num_dependents: int = 0
    num_languages: int = 0
    parent_max_education_ordinal: int | None = None
    # Academic info
    primary_undergrad_school: str | None = None
    primary_major: str | None = None
    highest_degree: str | None = None
    num_schools: int | None = None
    num_courses: int | None = None
    total_credit_hours: float | None = None
    # Military
    military_service_desc: str | None = None
    military_status_desc: str | None = None
    # Siblings
    num_siblings: int | None = None


class ExperienceHoursSummary(BaseModel):
    """Structured hours breakdown from AMCAS experience data."""
    total: float = 0
    research: float = 0
    volunteer_med: float = 0
    volunteer_non_med: float = 0
    employ_med: float = 0
    shadowing: float = 0
    community_service: float = 0
    healthcare: float = 0
    # Computed composites
    total_volunteer: float = 0
    clinical_total: float = 0


class ExperienceItem(BaseModel):
    """A single experience entry."""
    exp_type: str | None = None
    exp_name: str | None = None
    hours: float | None = None
    description: str | None = None


class ExperienceFlags(BaseModel):
    """9 binary experience flags."""
    has_direct_patient_care: bool = False
    has_volunteering: bool = False
    has_community_service: bool = False
    has_shadowing: bool = False
    has_clinical_experience: bool = False
    has_leadership: bool = False
    has_research: bool = False
    has_military_service: bool = False
    has_honors: bool = False


class EssaySection(BaseModel):
    """A single essay prompt and its text."""
    prompt_name: str
    text: str


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
    # New fields
    profile: ApplicantProfile | None = None
    experience_hours: ExperienceHoursSummary | None = None
    experience_items: list[ExperienceItem] = []
    experience_flags: ExperienceFlags | None = None
    personal_statement: str | None = None
    secondary_essays: list[EssaySection] = []


class FlagInfo(BaseModel):
    reason: str
    notes: str = ""
    flagged_at: str | None = None
