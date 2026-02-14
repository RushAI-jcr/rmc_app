"""Configuration for Rush Medical College Admissions Triage Pipeline."""

from pathlib import Path

# -- Paths ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "data" / "models"
CACHE_DIR = PROJECT_ROOT / "data" / "cache"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# -- Year folders (flat under data/raw/{year}/) -----------------------------
YEAR_FOLDERS = {
    2022: "2022",
    2023: "2023",
    2024: "2024",
}

# Files to load per year
FILE_MAP = {
    "applicants": "1. Applicants.xlsx",
    "language": "2. Language.xlsx",
    "parents": "3. Parents.xlsx",
    "siblings": "4. Siblings.xlsx",
    "academic_records": "5. Academic Records.xlsx",
    "experiences": "6. Experiences.xlsx",
    "schools": "8. School.xlsx",
    "personal_statement": "9. Personal Statement.xlsx",
    "secondary_application": "10. Secondary Application.xlsx",
    "military": "11. Military.xlsx",
    "gpa_trend": "12. GPA Trend.xlsx",
}

# -- Column name mappings ---------------------------------------------------
ID_COLUMN = "Amcas_ID"
ID_ALIASES = ["Amcas_ID", "amcas_id", "AMCAS ID", "AMCAS_ID"]

# Target columns
TARGET_SCORE = "Application_Review_Score"
TARGET_BUCKET = "Service_Rating_Categorical"
TARGET_BUCKET_NUM = "Service_Rating_Numerical"

# Bucket mapping
BUCKET_MAP = {
    "Lacking": 0,
    "Does Not Meet": 0,
    "Lacking/Does Not Meet": 0,
    "Adequate": 1,
    "Significant": 2,
    "Exceptional": 3,
    "lacking": 0,
    "does not meet": 0,
    "lacking/does not meet": 0,
    "adequate": 1,
    "significant": 2,
    "exceptional": 3,
}
BUCKET_LABELS = ["Lacking", "Adequate", "Significant", "Exceptional"]

# -- Triage tiers ----------------------------------------------------------
# DESIGN GOAL: Reduce 17,000 AMCAS applications → 4,000-5,000 for human review (~30% reduction)
#
# ACTUAL DISTRIBUTION (2024 test set, n=613):
#   Tier 0 (0-6.25):     17.0% (low alignment, AI filters out)
#   Tier 1 (6.25-12.5):  11.6% (borderline, optional review)
#   Tier 2 (12.5-18.75): 20.9% (strong alignment, recommended for review)
#   Tier 3 (18.75-25):   50.6% (high priority, always reviewed)
#
# Current behavior: Tier 2 & 3 = 71.5% of applicants proceed to human review
# This means AI is currently filtering out ~29% (Tier 0 & 1), meeting the goal.
#
# The high proportion in Tier 3 (50%) reflects Rush's pre-screened applicant pool.
# Median score is 19.0 (above the Tier 3 threshold of 18.75).
#
# NOTE: Thresholds should be recalibrated on full 17K pool if distribution differs.
SCORE_BUCKET_THRESHOLDS = [6.25, 12.5, 18.75]
TIER_LABELS = [
    "Not for Human Review",
    "Borderline — May Review",
    "Recommended for Review",
    "High Priority for Review"
]
TIER_COLORS = {0: "#ef4444", 1: "#f59e0b", 2: "#10b981", 3: "#3b82f6"}

# -- Two-stage screening model config ---------------------------------------
LOW_SCORE_THRESHOLD = 15  # Bottom 25th percentile; defines "low-scorer"
PRODUCTION_POOL_SIZE = 10000  # Expected applicant pool for K-scaling
PRODUCTION_K = 4000  # Number of candidates to select for human review
GATE_RECALL_TARGET = 0.95  # Minimum recall for low-scorers at gate
GATE_MAX_DEPTH = 2  # XGBoost tree depth (depth-2 optimal for n=1,303)
RANKER_MAX_DEPTH = 3  # Ranker tree depth (slightly deeper, trained on ~807)
RANKER_QUANTILE_ALPHA = 0.25  # Predict 25th percentile (conservative)

# NOTE: SES_Value, First_Generation_Ind, Disadvantaged_Ind appear in both
# BINARY_FEATURES (model inputs) and PROTECTED_ATTRIBUTES (fairness audit).
# This is intentional: AAMC holistic review encourages considering socioeconomic
# disadvantage. Only DEMOGRAPHICS_FOR_FAIRNESS_ONLY (Gender, Age, Race,
# Citizenship) are strictly blocked from model features.

# -- Structured features (NEVER include Age, Gender, Race, Ethnicity, Citizenship) --
NUMERIC_FEATURES = [
    "Exp_Hour_Total",
    "Exp_Hour_Research",
    "Exp_Hour_Volunteer_Med",
    "Exp_Hour_Volunteer_Non_Med",
    "Exp_Hour_Employ_Med",
    "Exp_Hour_Shadowing",
    "Comm_Service_Total_Hours",
    "HealthCare_Total_Hours",
    "Num_Languages",
    "Parent_Max_Education_Ordinal",
    "Num_Dependents",
]

BINARY_FEATURES = [
    "First_Generation_Ind",
    "Disadvantaged_Ind",
    "SES_Value",
    "Pell_Grant",
    "Fee_Assistance_Program",
    "Military_Service",
    "Childhood_Med_Underserved",
    "Paid_Employment_BF_18",
    "Contribution_to_Family",
    "Employed_Undergrad",
]

STRUCTURED_FEATURES = NUMERIC_FEATURES + BINARY_FEATURES

# -- Engineered features (reviewer-aligned composites) ----------------------
ENGINEERED_FEATURES = [
    "Total_Volunteer_Hours",
    "Community_Engaged_Ratio",
    "Clinical_Total_Hours",
    "Direct_Care_Ratio",
    "Adversity_Count",
    "Grit_Index",
    "Experience_Diversity",
]

# -- Columns to drop during cleaning (>70% missing or uninformative) --------
COLUMNS_TO_DROP = [
    "Eo_Level",
    "Prev_Applied_Rush",
    "Hrdshp_Comments",
    "Prev_Matric_Desc",
    "Prev_Matric_Year",
    "Prev_Matric_School",
    "Prev_Matric_Degree",
    "Prev_Matric_Status",
    "Military_Service_Status",
    "Military_Discharge_Desc",
    "Felony_Desc",
    "GPA_Trend_Ordinal",
    "Total_GPA_Trend",
    "BCPM_GPA_Trend",
]

# -- 9 binary experience flags ---------------------------------------------
EXPERIENCE_BINARY_FLAGS = [
    "has_direct_patient_care",
    "has_volunteering",
    "has_community_service",
    "has_shadowing",
    "has_clinical_experience",
    "has_leadership",
    "has_research",
    "has_military_service",
    "has_honors",
]

# -- Experience type -> binary flag mapping ---------------------------------
EXP_TYPE_TO_FLAG = {
    "Physician Shadowing/Clinical Observation": "has_shadowing",
    "Community Service/Volunteer - Medical/Clinical": "has_volunteering",
    "Community Service/Volunteer - Not Medical/Clinical": "has_community_service",
    "Paid Employment - Medical/Clinical": "has_clinical_experience",
    "Research/Lab": "has_research",
    "Leadership - Not Listed Elsewhere": "has_leadership",
    "Military Service": "has_military_service",
}

PATIENT_CARE_EXP_TYPES = [
    "Physician Shadowing/Clinical Observation",
    "Paid Employment - Medical/Clinical",
    "Community Service/Volunteer - Medical/Clinical",
]

# -- GPA trend ordinal mapping ----------------------------------------------
GPA_TREND_MAP = {
    "Downward": 0,
    "Stable": 1,
    "Upward": 2,
}

# -- Parent education ordinal mapping ---------------------------------------
PARENT_EDUCATION_MAP = {
    "Less Than High School": 0,
    "High School Graduate (high school diploma or equivalent)": 1,
    "Some college, but no degree": 2,
    "Associates Degree (AS,AN,etc.)": 3,
    "Bachelor Degree (BA,BS,etc)": 4,
    "Some graduate,but no degree": 5,
    "Masters Degree": 5,
    "Don't know": 2,
    "Doctorate of Medicine (MD)": 6,
    "Doctor of Philosophy (Phd)": 6,
    "Doctor of Jurisprudence": 6,
    "MD/PhD": 6,
    "Doctor of Pharmacy": 6,
    "Other Doctorate Degree": 6,
    "Doctor of Dental Science(DDS,DMD)": 6,
    "Doctor of Veterinary Medicine": 6,
    "Doctor of Chiropractic": 6,
    "Doctor of Science": 6,
    "Doctor of Education": 6,
    "Doctor of Osteopathic Medicine/Osteopathy(DO)": 6,
    "Doctor of Optometry": 6,
    "Doctor of Podiatric Medicine/Podiatry": 6,
}

# -- LLM rubric dimensions (v2: atomic scoring, 1-4 scale) -----------------
# v2 uses research-grounded atomic prompts (1 dimension per API call)
# to eliminate halo effects. Scale: 1-4 (no neutral midpoint).
# Research: ACL 2024 (LLM-Rubric), EMNLP 2023 (G-Eval), arxiv:2509.21910 (AutoSCORE)

PS_DIMS = [
    "writing_quality",
    "authenticity_and_self_awareness",
    "mission_alignment_service_orientation",
    "adversity_resilience",
    "motivation_depth",
    "intellectual_curiosity",
    "maturity_and_reflection",
]

EXPERIENCE_QUALITY_DIMS = [
    "direct_patient_care_depth_and_quality",
    "research_depth_and_quality",
    "community_service_depth_and_quality",
    "leadership_depth_and_quality",
    "teaching_mentoring_depth_and_quality",
    "clinical_exposure_depth_and_quality",
    "clinical_employment_depth_and_quality",
    "advocacy_policy_depth_and_quality",
    "global_crosscultural_depth_and_quality",
]

SECONDARY_DIMS = [
    "personal_attributes_insight",
    "adversity_response_quality",
    "reflection_depth",
    "healthcare_experience_quality",
    "research_depth",
]

ALL_RUBRIC_DIMS = PS_DIMS + EXPERIENCE_QUALITY_DIMS + SECONDARY_DIMS

# Curated 7-dimension rubric: domain expertise + statistical signal
# Selected by admissions department priorities (community service, patient care,
# mission alignment, resilience/grit) combined with top residual-correlated dims
# from n=101 pilot test (leadership, motivation).
# Performance: R2=+0.050, MAE improvement +0.31 vs Plan A (n=101 LOO-CV stacking)
# Cost: 7 API calls per applicant vs 21 (67% reduction)
CURATED_RUBRIC_DIMS = [
    # PS dimensions (3 calls)
    "mission_alignment_service_orientation",  # Admissions dept priority
    "adversity_resilience",                   # Resilience/grit + stat significant (p=0.010)
    "motivation_depth",                       # Stat top-5 residual correlation
    # Experience dimensions (3 calls)
    "community_service_depth_and_quality",    # Admissions dept priority
    "direct_patient_care_depth_and_quality",  # Admissions dept priority + stat top-5
    "leadership_depth_and_quality",           # Stat #1 residual correlation (p=0.023)
    # Secondary dimensions (1 call)
    "adversity_response_quality",             # Stat #2 residual correlation (p=0.006)
]

# -- Model training config --------------------------------------------------
TRAIN_YEARS = [2022, 2023]
TEST_YEAR = 2024
RANDOM_STATE = 42

# -- Model configurations ---------------------------------------------------
WORKING_PKLS = {
    "A_Structured": "results_A_Structured.pkl",
    "D_Struct+Rubric": "results_D_Struct+Rubric.pkl",
}

CONFIG_LABELS = {
    "A_Structured": "Plan A: Structured Only",
    "D_Struct+Rubric": "Plan B: Structured + LLM Rubric",
}

CONFIG_SHORT = {
    "A_Structured": "Plan A",
    "D_Struct+Rubric": "Plan B",
}

# -- Protected attributes (fairness audit only, NEVER model features) -------
PROTECTED_ATTRIBUTES = [
    "Gender",
    "Age",
    "Citizenship",
    "Race",
    "SES_Value",
    "First_Generation_Ind",
    "Disadvantaged_Ind",
]

DEMOGRAPHICS_FOR_FAIRNESS_ONLY = {"Gender", "Age", "Race", "Citizenship"}

# -- Secondary application essay columns ------------------------------------
SECONDARY_ESSAY_COLUMNS = [
    "1 - Personal Attributes / Life Experiences",
    "2 - Challenging Situation",
    "3 - Reflect Experience",
    "4 - Hope to Gain",
    "6 - Direct Care Experience",
    "7 - COVID Impact",
]

# -- Display names ----------------------------------------------------------
FEATURE_DISPLAY_NAMES = {
    "writing_quality": "Writing Quality",
    "authenticity_and_self_awareness": "Self-Awareness & Authenticity",
    "mission_alignment_service_orientation": "Mission Alignment",
    "adversity_resilience": "Adversity & Resilience",
    "motivation_depth": "Motivation Depth",
    "intellectual_curiosity": "Intellectual Curiosity",
    "maturity_and_reflection": "Maturity & Reflection",
    "personal_attributes_insight": "Personal Insight",
    "adversity_response_quality": "Adversity Response",
    "reflection_depth": "Reflection Depth",
    "healthcare_experience_quality": "Healthcare Commitment",
    "research_depth": "Research Depth (Secondary)",
    "Exp_Hour_Total": "Total Exp Hours",
    "Exp_Hour_Research": "Research Hours",
    "Exp_Hour_Volunteer_Med": "Med Volunteer Hours",
    "Exp_Hour_Volunteer_Non_Med": "Non-Med Volunteer Hours",
    "Exp_Hour_Employ_Med": "Med Employment Hours",
    "Exp_Hour_Shadowing": "Shadowing Hours",
    "Comm_Service_Total_Hours": "Community Service Hours",
    "HealthCare_Total_Hours": "Healthcare Hours",
    "Num_Languages": "Languages Spoken",
    "Parent_Max_Education_Ordinal": "Parent Education Level",
    "First_Generation_Ind": "First Generation",
    "Disadvantaged_Ind": "Disadvantaged Status",
    "SES_Value": "Socioeconomic Status",
    "Pell_Grant": "Pell Grant",
    "Fee_Assistance_Program": "Fee Assistance",
    "Military_Service": "Military Service",
    "Total_Volunteer_Hours": "Total Volunteer Hours",
    "Community_Engaged_Ratio": "Community-Engaged Ratio",
    "Clinical_Total_Hours": "Total Clinical Hours",
    "Direct_Care_Ratio": "Direct Care Ratio",
    "Adversity_Count": "Adversity Indicator Count",
    "Grit_Index": "Grit Index",
    "Experience_Diversity": "Experience Diversity",
    "Num_Dependents": "Number of Dependents",
    "Childhood_Med_Underserved": "Childhood Med Underserved",
    "Paid_Employment_BF_18": "Paid Employment Before 18",
    "Contribution_to_Family": "Contributed to Family",
    "Employed_Undergrad": "Employed as Undergrad",
    "rubric_scored_flag": "Had Rubric Scores",
    # v2 experience dimensions
    "direct_patient_care_depth_and_quality": "Patient Care Depth",
    "research_depth_and_quality": "Research Depth",
    "community_service_depth_and_quality": "Community Service Depth",
    "leadership_depth_and_quality": "Leadership Depth",
    "teaching_mentoring_depth_and_quality": "Teaching & Mentoring",
    "clinical_exposure_depth_and_quality": "Clinical Exposure",
    "clinical_employment_depth_and_quality": "Clinical Employment",
    "advocacy_policy_depth_and_quality": "Advocacy & Policy",
    "global_crosscultural_depth_and_quality": "Global / Cross-Cultural",
}




def prettify(name: str) -> str:
    """Return a human-readable display name for a feature."""
    return FEATURE_DISPLAY_NAMES.get(name, name.replace("_", " ").title())


def score_to_tier(score: float) -> int:
    """Map a 0-25 score to a triage tier (0-3)."""
    for i, threshold in enumerate(SCORE_BUCKET_THRESHOLDS):
        if score < threshold:
            return i
    return 3
