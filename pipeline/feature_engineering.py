"""Feature engineering: structured features, engineered composites, rubric scores."""

import json
import logging
from pathlib import Path

import pandas as pd
import numpy as np

from pipeline.config import (
    ID_COLUMN,
    NUMERIC_FEATURES,
    BINARY_FEATURES,
    EXPERIENCE_BINARY_FLAGS,
    DEMOGRAPHICS_FOR_FAIRNESS_ONLY,
    ALL_RUBRIC_DIMS_V1,
    RUBRIC_FEATURES_FINAL,
    CACHE_DIR,
    PROCESSED_DIR,
)

logger = logging.getLogger(__name__)


def extract_structured_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract the ~15 structured features from the unified dataset."""
    features = pd.DataFrame()
    features[ID_COLUMN] = df[ID_COLUMN]

    # Numeric features
    active_numeric = [col for col in NUMERIC_FEATURES if col in df.columns]
    skipped_numeric = set(NUMERIC_FEATURES) - set(active_numeric)
    if skipped_numeric:
        logger.info("Skipping numeric features not in data: %s", skipped_numeric)

    for col in active_numeric:
        features[col] = pd.to_numeric(df[col], errors="coerce")

    # Binary features with alias handling for typos
    _BINARY_ALIASES = {
        "Disadvantaged_Ind": ["Disadvantanged_Ind", "Disadvantaged_Ind"],
    }

    def _to_binary(series: pd.Series) -> pd.Series:
        if series.dtype in (int, float, np.int64, np.float64):
            return series.fillna(0).astype(int)
        return series.map(
            lambda x: 1 if str(x).strip().lower().startswith("y") else 0
        )

    for col in BINARY_FEATURES:
        matched = False
        candidates = _BINARY_ALIASES.get(col, []) + [col]
        for candidate in candidates:
            if candidate in df.columns:
                features[col] = _to_binary(df[candidate])
                matched = True
                break
        if not matched:
            logger.warning("Missing binary feature: %s", col)
            features[col] = 0

    # Fill NaN in numeric features
    for col in active_numeric:
        features[col] = features[col].fillna(0.0)

    actual_features = [c for c in features.columns if c != ID_COLUMN]
    logger.info(
        "Extracted %d structured features for %d applicants",
        len(actual_features),
        len(features),
    )
    return features


def engineer_composite_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create reviewer-aligned composite features.

    - Total_Volunteer_Hours = Med + Non-Med volunteer hours
    - Community_Engaged_Ratio = Non-Med / Total volunteer (0 if none)
    - Clinical_Total_Hours = Shadowing + Med Employment
    - Direct_Care_Ratio = Med Employment / Clinical Total (0 if none)
    - Adversity_Count = sum of 5 grit indicators
    """
    out = pd.DataFrame()
    out[ID_COLUMN] = df[ID_COLUMN]

    # Volunteering composites
    med_vol = df.get("Exp_Hour_Volunteer_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
    non_med_vol = df.get("Exp_Hour_Volunteer_Non_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
    out["Total_Volunteer_Hours"] = med_vol + non_med_vol
    out["Community_Engaged_Ratio"] = np.where(
        out["Total_Volunteer_Hours"] > 0,
        non_med_vol / out["Total_Volunteer_Hours"],
        0.0,
    )

    # Clinical composites
    shadowing = df.get("Exp_Hour_Shadowing", pd.Series(0, index=df.index)).fillna(0).astype(float)
    med_employ = df.get("Exp_Hour_Employ_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
    out["Clinical_Total_Hours"] = shadowing + med_employ
    out["Direct_Care_Ratio"] = np.where(
        out["Clinical_Total_Hours"] > 0,
        med_employ / out["Clinical_Total_Hours"],
        0.0,
    )

    # Adversity count (original 5 indicators)
    grit_cols = ["First_Generation_Ind", "Disadvantaged_Ind", "SES_Value", "Pell_Grant", "Fee_Assistance_Program"]
    adversity_sum = pd.Series(0, index=df.index, dtype=float)
    for col in grit_cols:
        if col in df.columns:
            adversity_sum = adversity_sum + pd.to_numeric(df[col], errors="coerce").fillna(0)
    out["Adversity_Count"] = adversity_sum.astype(int)

    # Grit Index (broader: adversity + employment + family + underserved)
    grit_extra = ["Paid_Employment_BF_18", "Contribution_to_Family", "Childhood_Med_Underserved"]
    grit_total = adversity_sum.copy()
    for col in grit_extra:
        if col in df.columns:
            grit_total = grit_total + pd.to_numeric(df[col], errors="coerce").fillna(0)
    out["Grit_Index"] = grit_total.astype(int)

    # Experience Diversity (count of binary experience flags that are 1)
    exp_flag_cols = [
        "has_direct_patient_care", "has_volunteering", "has_community_service",
        "has_shadowing", "has_clinical_experience", "has_leadership",
        "has_research", "has_military_service", "has_honors",
    ]
    diversity_sum = pd.Series(0, index=df.index, dtype=float)
    for col in exp_flag_cols:
        if col in df.columns:
            diversity_sum = diversity_sum + pd.to_numeric(df[col], errors="coerce").fillna(0)
    out["Experience_Diversity"] = diversity_sum.astype(int)

    logger.info("Engineered 7 composite features for %d applicants", len(out))
    return out


def extract_binary_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Extract the 9 binary experience flags already derived during ingestion."""
    flag_cols = [col for col in EXPERIENCE_BINARY_FLAGS if col in df.columns]
    missing = set(EXPERIENCE_BINARY_FLAGS) - set(flag_cols)
    if missing:
        logger.warning("Missing binary flag columns: %s", missing)

    flags = df[[ID_COLUMN] + flag_cols].copy()
    for col in EXPERIENCE_BINARY_FLAGS:
        if col not in flags.columns:
            flags[col] = 0

    return flags


def load_rubric_features(rubric_path: Path | None = None) -> pd.DataFrame:
    """Load rubric scores from cached JSON and collapse to final feature set.

    v2: All experience domains are scored on 1-5 depth/quality scales by the
    LLM rubric scorer (pipeline/rubric_scorer.py), replacing binary flags.
    New dimensions: research_publication_quality, military_service_depth.

    Zeros in quality dims (1-5 scale) are treated as missing and imputed
    with the median of non-zero values.
    """
    rubric_path = rubric_path or (CACHE_DIR / "rubric_scores.json")
    if not rubric_path.exists():
        logger.warning("Rubric scores not found at %s", rubric_path)
        return pd.DataFrame()

    with open(rubric_path) as f:
        rubric_data = json.load(f)

    # Load all raw dims first
    rows = []
    for amcas_id, scores in rubric_data.items():
        row = {ID_COLUMN: int(amcas_id)}
        for dim in ALL_RUBRIC_DIMS_V1:
            row[dim] = scores.get(dim, 0)
        rows.append(row)

    raw_df = pd.DataFrame(rows)
    logger.info("Loaded raw rubric scores: %d applicants, %d dims", len(raw_df), len(ALL_RUBRIC_DIMS_V1))

    # Save raw version for reference
    raw_path = PROCESSED_DIR / "rubric_features_raw.csv"
    raw_df.to_csv(raw_path, index=False)

    # Collapse to final feature set — keep all depth/quality dims (1-5 scale)
    collapsed = pd.DataFrame()
    collapsed[ID_COLUMN] = raw_df[ID_COLUMN]

    # All quality dims to keep from RUBRIC_FEATURES_FINAL (excluding rubric_scored_flag)
    quality_dims = [dim for dim in RUBRIC_FEATURES_FINAL if dim != "rubric_scored_flag"]

    for dim in quality_dims:
        if dim in raw_df.columns:
            col_data = raw_df[dim].copy()
        else:
            # Dimension not yet scored (e.g., new v2 dims not in old cache)
            logger.info("Dimension %s not in rubric cache, defaulting to 0", dim)
            col_data = pd.Series(0, index=raw_df.index)

        # Treat 0 as missing for quality scales, impute with median of non-zero
        non_zero = col_data[col_data > 0]
        median_val = float(non_zero.median()) if len(non_zero) > 0 else 3.0
        collapsed[dim] = col_data.replace(0, median_val)

    # Binary flag: was applicant scored at all (writing_quality > 0 in raw data)
    collapsed["rubric_scored_flag"] = (raw_df["writing_quality"] > 0).astype(int)

    # Save collapsed version
    out_path = PROCESSED_DIR / "rubric_features.csv"
    collapsed.to_csv(out_path, index=False)

    n_scored = int(collapsed["rubric_scored_flag"].sum())
    logger.info(
        "Collapsed rubric: %d features, %d/%d applicants fully scored",
        len(collapsed.columns) - 1, n_scored, len(collapsed),
    )

    return collapsed


def combine_feature_sets(
    structured: pd.DataFrame,
    engineered: pd.DataFrame | None = None,
    binary_flags: pd.DataFrame | None = None,
    rubric_scores: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Merge multiple feature sets into a single feature matrix."""
    combined = structured.copy()

    for aux_df in [engineered, binary_flags, rubric_scores]:
        if aux_df is not None:
            combined = combined.merge(aux_df, on=ID_COLUMN, how="left", suffixes=("", "_dup"))
            combined = combined.drop(columns=[c for c in combined.columns if c.endswith("_dup")])

    logger.info(
        "Combined feature matrix: %d applicants, %d features",
        len(combined),
        len(combined.columns) - 1,
    )
    return combined


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return all feature column names (excluding ID, targets, demographics)."""
    exclude = {
        ID_COLUMN,
        "Application_Review_Score",
        "Service_Rating_Categorical",
        "Service_Rating_Numerical",
        "bucket_label",
        "app_year",
        "App_Year",
    }
    feature_cols = [c for c in df.columns if c not in exclude and not c.startswith("_")]
    forbidden = set(feature_cols) & DEMOGRAPHICS_FOR_FAIRNESS_ONLY
    if forbidden:
        raise ValueError(
            f"Feature list must not include demographics (fairness-only): {forbidden}"
        )
    return feature_cols
