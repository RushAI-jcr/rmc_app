"""Applicant endpoints: list and detail with scorecard data."""

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from api.db.models import User
from api.db.session import get_db
from api.dependencies import get_current_user
from api.models.applicant import (
    ApplicantSummary,
    ApplicantDetail,
    ApplicantProfile,
    ExperienceHoursSummary,
    ExperienceItem,
    ExperienceFlags,
    EssaySection,
    RubricScorecard,
    RubricGroup,
    RubricDimension,
    RubricDimensionDetail,
    ShapDriver,
    FlagInfo,
)
from api.services.audit_service import log_action
from api.services.prediction_service import compute_shap_for_applicant, get_test_predictions
from api.services.review_service import get_decision_for_applicant
from api.utils.nan_helpers import safe_bool, safe_float, safe_int, safe_str

router = APIRouter(prefix="/api/applicants", tags=["applicants"])


# ---------------------------------------------------------------------------
# Rubric grouping
# ---------------------------------------------------------------------------

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

# Secondary essay column -> display name mapping
SECONDARY_ESSAY_DISPLAY = {
    "1_-_Personal_Attributes_/_Life_Experiences": "Personal Attributes / Life Experiences",
    "2_-_Challenging_Situation": "Challenging Situation",
    "3_-_Reflect_Experience": "Reflect on Experience",
    "4_-_Hope_to_Gain": "Hope to Gain",
    "6_-_Direct_Care_Experience": "Direct Care Experience",
    "7_-_COVID_Impact": "COVID Impact",
}


def _build_rubric_scorecard(
    rubric_data: dict,
    rubric_details: dict | None = None,
) -> RubricScorecard:
    """Build a reviewer-grouped rubric scorecard from raw rubric data."""
    groups = []
    has_any = False
    details = rubric_details or {}
    for group_def in RUBRIC_GROUPS:
        dimensions = []
        for dim_key, display_name in group_def["dims"]:
            score = rubric_data.get(dim_key, 0)
            if score > 0:
                has_any = True
            dim_detail = None
            if dim_key in details:
                d = details[dim_key]
                dim_detail = RubricDimensionDetail(
                    evidence_extracted=d.get("evidence_extracted", ""),
                    reasoning=d.get("reasoning", ""),
                )
            dimensions.append(RubricDimension(
                name=display_name,
                score=float(score),
                detail=dim_detail,
            ))
        groups.append(RubricGroup(label=group_def["label"], dimensions=dimensions))
    return RubricScorecard(groups=groups, has_rubric=has_any)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("")
def list_applicants(
    request: Request,
    config: str = Query("A_Structured"),
    tier: int | None = None,
    search: str | None = None,
    cycle_year: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Paginated list of applicants with predictions."""
    store = request.app.state.store
    log_action(db, current_user.id, "list_applicants", resource_type="applicant")
    predictions = store.get_predictions(config)

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApplicantDetail:
    """Full scorecard for a single applicant."""
    store = request.app.state.store
    log_action(db, current_user.id, "view_applicant", resource_type="applicant", resource_id=str(amcas_id))
    predictions = store.get_predictions(config)

    match = next((p for p in predictions if p["amcas_id"] == amcas_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Applicant {amcas_id} not found")

    # SHAP drivers and class probabilities — admin-only (model internals)
    is_admin = current_user.role == "admin"
    shap_drivers: list[dict] = compute_shap_for_applicant(config, amcas_id, store) if is_admin else []

    class_probs: list[float] = []
    if is_admin:
        preds = get_test_predictions(config, store)
        if preds and preds["clf_proba"] is not None:
            for i, tid in enumerate(preds["test_ids"]):
                if int(tid) == amcas_id:
                    class_probs = preds["clf_proba"][i].tolist()
                    break

    # Rubric scorecard (reviewer-grouped) with v2 details
    scorecard = None
    rubric_data = store.rubric_scores.get(str(amcas_id))
    rubric_details = store.rubric_details.get(str(amcas_id))
    if rubric_data:
        scorecard = _build_rubric_scorecard(rubric_data, rubric_details)

    # Flag info (if previously flagged) — now from PostgreSQL
    flag_info = None
    cycle_year = match.get("app_year", 2024)
    decision_row = get_decision_for_applicant(db, amcas_id, cycle_year)
    if decision_row and decision_row.decision == "flag":
        flag_info = FlagInfo(
            reason=decision_row.flag_reason or "",
            notes=decision_row.notes or "",
            flagged_at=decision_row.created_at.isoformat() if decision_row.created_at else None,
        )

    # --- Build profile, experience, essay data from master_data ---
    profile = None
    experience_hours = None
    experience_items_list: list[ExperienceItem] = []
    experience_flags = None
    personal_statement_text = None
    secondary_essays: list[EssaySection] = []

    # Look up in master_data
    md = store.master_data
    if not md.empty:
        row_df = md[md["Amcas_ID"] == amcas_id]
        if not row_df.empty:
            r = row_df.iloc[0]

            # Demographics from DEMOGRAPHICS_FOR_FAIRNESS_ONLY are admin-only
            profile = ApplicantProfile(
                age=safe_int(r.get("Age"), 0) or None if is_admin else None,
                gender=safe_str(r.get("Gender")) if is_admin else None,
                citizenship=safe_str(r.get("Citizenship")) if is_admin else None,
                ses_value=safe_int(r.get("SES_Value"), 0) or None,
                first_generation=safe_bool(r.get("First_Generation_Ind")),
                disadvantaged=safe_bool(r.get("Disadvantaged_Ind", r.get("Disadvantanged_Ind"))),
                pell_grant=safe_bool(r.get("Pell_Grant")),
                fee_assistance=safe_bool(r.get("Fee_Assistance_Program")),
                military_service=safe_bool(r.get("Military_Service")),
                childhood_med_underserved=safe_bool(r.get("Childhood_Med_Underserved")),
                paid_employment_bf_18=safe_bool(r.get("Paid_Employment_BF_18")),
                contribution_to_family=safe_bool(r.get("Contribution_to_Family")),
                employed_undergrad=safe_bool(r.get("Employed_Undergrad")),
                num_dependents=safe_int(r.get("Num_Dependents")),
                num_languages=safe_int(r.get("Num_Languages")),
                parent_max_education_ordinal=safe_int(r.get("Parent_Max_Education_Ordinal"), -1) if pd.notna(r.get("Parent_Max_Education_Ordinal")) else None,
                primary_undergrad_school=safe_str(r.get("Under_School")) or safe_str(r.get("Primary_Undergrad_School")),
                primary_major=safe_str(r.get("Major_Long_Desc")) or safe_str(r.get("Primary_Major")),
                highest_degree=safe_str(r.get("Highest_Degree")),
                num_schools=safe_int(r.get("Num_Schools"), 0) or None,
                num_courses=safe_int(r.get("Num_Courses"), 0) or None,
                total_credit_hours=safe_float(r.get("Total_Credit_Hours")) or None,
                military_service_desc=safe_str(r.get("Military_Service_Desc")),
                military_status_desc=safe_str(r.get("Military_Status_Desc")),
                num_siblings=safe_int(r.get("Num_Siblings"), 0) or None,
            )

            experience_hours = ExperienceHoursSummary(
                total=safe_float(r.get("Exp_Hour_Total")),
                research=safe_float(r.get("Exp_Hour_Research")),
                volunteer_med=safe_float(r.get("Exp_Hour_Volunteer_Med")),
                volunteer_non_med=safe_float(r.get("Exp_Hour_Volunteer_Non_Med")),
                employ_med=safe_float(r.get("Exp_Hour_Employ_Med")),
                shadowing=safe_float(r.get("Exp_Hour_Shadowing")),
                community_service=safe_float(r.get("Comm_Service_Total_Hours")),
                healthcare=safe_float(r.get("HealthCare_Total_Hours")),
                total_volunteer=safe_float(r.get("Total_Volunteer_Hours")),
                clinical_total=safe_float(r.get("Clinical_Total_Hours")),
            )

            experience_flags = ExperienceFlags(
                has_direct_patient_care=safe_bool(r.get("has_direct_patient_care")),
                has_volunteering=safe_bool(r.get("has_volunteering")),
                has_community_service=safe_bool(r.get("has_community_service")),
                has_shadowing=safe_bool(r.get("has_shadowing")),
                has_clinical_experience=safe_bool(r.get("has_clinical_experience")),
                has_leadership=safe_bool(r.get("has_leadership")),
                has_research=safe_bool(r.get("has_research")),
                has_military_service=safe_bool(r.get("has_military_service")),
                has_honors=safe_bool(r.get("has_honors")),
            )

            # Personal statement
            personal_statement_text = safe_str(r.get("personal_statement"))

            # Secondary essays
            for col, display in SECONDARY_ESSAY_DISPLAY.items():
                text = safe_str(r.get(col))
                if text:
                    secondary_essays.append(EssaySection(prompt_name=display, text=text))

    # Load raw experience items from experiences_data (vectorized, no iterrows)
    exp_df = store.experiences_data
    if not exp_df.empty:
        applicant_exps = exp_df.loc[exp_df["Amcas_ID"] == amcas_id]
        for rec in applicant_exps.to_dict("records"):
            experience_items_list.append(ExperienceItem(
                exp_type=safe_str(rec.get("Exp_Type")),
                exp_name=safe_str(rec.get("Exp_Name")),
                hours=safe_float(rec.get("Hours")) if pd.notna(rec.get("Hours")) else None,
                description=safe_str(rec.get("Exp_Desc")),
            ))

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
        profile=profile,
        experience_hours=experience_hours,
        experience_items=experience_items_list,
        experience_flags=experience_flags,
        personal_statement=personal_statement_text,
        secondary_essays=secondary_essays,
    )
