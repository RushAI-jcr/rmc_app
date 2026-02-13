"""Applicant endpoints: list and detail with scorecard data."""

from fastapi import APIRouter, HTTPException, Query, Request

from api.config import (
    TIER_LABELS,
    TIER_COLORS,
    prettify,
)
from api.models.applicant import (
    ApplicantSummary,
    ApplicantDetail,
    RubricScorecard,
    RubricGroup,
    RubricDimension,
    ShapDriver,
    FlagInfo,
)
from api.services.prediction_service import build_prediction_table, compute_shap_for_applicant

router = APIRouter(prefix="/api/applicants", tags=["applicants"])

# Reviewer-priority rubric grouping (built from v2 dimension constants)
def _build_rubric_groups() -> list[dict]:
    """Build RUBRIC_GROUPS from v2 dimension constants."""
    return [
        {
            "label": "Personal Statement",
            "dims": [
                ("writing_quality", "Writing Quality"),
                ("authenticity_and_self_awareness", "Authenticity & Self-Awareness"),
                ("mission_alignment_service_orientation", "Mission Alignment"),
                ("adversity_resilience", "Adversity & Resilience"),
                ("motivation_depth", "Motivation Depth"),
                ("intellectual_curiosity", "Intellectual Curiosity"),
                ("maturity_and_reflection", "Maturity & Reflection"),
            ],
        },
        {
            "label": "Experience Quality",
            "dims": [
                ("direct_patient_care_depth_and_quality", "Direct Patient Care"),
                ("research_depth_and_quality", "Research"),
                ("community_service_depth_and_quality", "Community Service"),
                ("leadership_depth_and_quality", "Leadership"),
                ("teaching_mentoring_depth_and_quality", "Teaching & Mentoring"),
                ("clinical_exposure_depth_and_quality", "Clinical Exposure"),
                ("clinical_employment_depth_and_quality", "Clinical Employment"),
                ("advocacy_policy_depth_and_quality", "Advocacy & Policy"),
                ("global_crosscultural_depth_and_quality", "Global & Cross-Cultural"),
            ],
        },
        {
            "label": "Secondary Essays",
            "dims": [
                ("personal_attributes_insight", "Personal Attributes"),
                ("adversity_response_quality", "Adversity Response"),
                ("reflection_depth", "Reflection Depth"),
                ("healthcare_experience_quality", "Healthcare Experience"),
                ("research_depth", "Research Depth"),
            ],
        },
    ]


RUBRIC_GROUPS = _build_rubric_groups()


def _build_rubric_scorecard(rubric_data: dict) -> RubricScorecard:
    """Build a reviewer-grouped rubric scorecard from raw rubric data."""
    groups = []
    has_any = False
    for group_def in RUBRIC_GROUPS:
        dimensions = []
        for dim_key, display_name in group_def["dims"]:
            score = rubric_data.get(dim_key, 0)
            if score > 0:
                has_any = True
            dimensions.append(RubricDimension(name=display_name, score=float(score)))
        groups.append(RubricGroup(label=group_def["label"], dimensions=dimensions))
    return RubricScorecard(groups=groups, has_rubric=has_any)


@router.get("")
def list_applicants(
    request: Request,
    config: str = Query("A_Structured"),
    tier: int | None = None,
    search: str | None = None,
    cycle_year: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> dict:
    """Paginated list of applicants with predictions."""
    store = request.app.state.store
    predictions = build_prediction_table(config, store)

    if cycle_year is not None:
        predictions = [p for p in predictions if p.get("app_year") == cycle_year]

    if tier is not None:
        predictions = [p for p in predictions if p["tier"] == tier]

    if search:
        predictions = [p for p in predictions if search in str(p["amcas_id"])]

    total = len(predictions)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = predictions[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [ApplicantSummary(**p).model_dump() for p in page_data],
    }


@router.get("/{amcas_id}")
def get_applicant(
    request: Request,
    amcas_id: int,
    config: str = Query("A_Structured"),
) -> ApplicantDetail:
    """Full scorecard for a single applicant."""
    store = request.app.state.store
    predictions = build_prediction_table(config, store)

    match = next((p for p in predictions if p["amcas_id"] == amcas_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Applicant {amcas_id} not found")

    # SHAP drivers
    shap_drivers = compute_shap_for_applicant(config, amcas_id, store)

    # Class probabilities
    from api.services.prediction_service import get_test_predictions
    preds = get_test_predictions(config, store)
    class_probs = []
    if preds and preds["clf_proba"] is not None:
        for i, tid in enumerate(preds["test_ids"]):
            if int(tid) == amcas_id:
                class_probs = preds["clf_proba"][i].tolist()
                break

    # Rubric scorecard (reviewer-grouped)
    scorecard = None
    rubric_data = store.rubric_scores.get(str(amcas_id))
    if rubric_data:
        scorecard = _build_rubric_scorecard(rubric_data)

    # Flag info (if previously flagged)
    flag_info = None
    decision_data = store.decisions.get(amcas_id, {})
    if decision_data.get("decision") == "flag":
        flag_info = FlagInfo(
            reason=decision_data.get("flag_reason", ""),
            notes=decision_data.get("notes", ""),
            flagged_at=decision_data.get("flagged_at"),
        )

    return ApplicantDetail(
        amcas_id=match["amcas_id"],
        tier=match["tier"],
        tier_label=match["tier_label"],
        tier_color=match["tier_color"],
        predicted_score=match["predicted_score"],
        predicted_bucket=match["predicted_bucket"],
        confidence=match["confidence"],
        clf_reg_agree=match["clf_reg_agree"],
        actual_score=match.get("actual_score"),
        actual_bucket=match.get("actual_bucket"),
        class_probabilities=class_probs,
        shap_drivers=[ShapDriver(**d) for d in shap_drivers],
        rubric_scorecard=scorecard,
        app_year=match.get("app_year"),
        flag=flag_info,
    )
