"""Score-only pipeline: predict with a pre-trained model (no retraining).

Usage:
    from pipeline.score_pipeline import score_new_cycle
    result = score_new_cycle(
        data_dir=Path("/tmp/uploads/session-123"),
        cycle_year=2025,
    )
"""

import logging
import pickle
from collections.abc import Callable
from pathlib import Path

import numpy as np

from pipeline.config import (
    ID_COLUMN,
    MODELS_DIR,
    PROCESSED_DIR,
    CACHE_DIR,
    SCORE_BUCKET_THRESHOLDS,
    TIER_LABELS,
)
from pipeline.data_ingestion import build_unified_dataset
from pipeline.data_cleaning import clean_dataset
from pipeline.feature_engineering import (
    extract_structured_features,
    engineer_composite_features,
    extract_binary_flags,
    load_rubric_features,
    combine_feature_sets,
)

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str, int], None]


def _noop_progress(_step: str, _pct: int) -> None:
    pass


def _score_to_tier(score: float) -> int:
    """Map a continuous score to a triage tier index (0-3)."""
    for i, threshold in enumerate(SCORE_BUCKET_THRESHOLDS):
        if score < threshold:
            return i
    return 3


def score_new_cycle(
    data_dir: Path,
    cycle_year: int,
    model_pkl: str = "results_A_Structured.pkl",
    file_map: dict[str, Path] | None = None,
    progress_callback: ProgressCallback | None = None,
    rubric_scores_path: Path | None = None,
) -> dict:
    """Run the score-only pipeline on a new cycle's data.

    Steps:
      1. Ingest (10%): load xlsx files into a unified DataFrame
      2. Clean (40%): apply data cleaning
      3. Features (60%): extract structured + engineered + binary flag features
      4. ML Score (80%): load pre-trained model, predict scores
      5. Triage (100%): assign tiers, save output

    Args:
        data_dir: Directory containing the uploaded xlsx files.
        cycle_year: The admissions cycle year (e.g. 2025).
        model_pkl: Filename of the pre-trained model pickle in MODELS_DIR.
        file_map: Optional mapping of logical file type -> exact Path.
        progress_callback: Called with (step_name, percent_complete).
        rubric_scores_path: Path to rubric_scores.json (if available).

    Returns:
        Dict with applicant_count, tier_distribution, output_path.
    """
    cb = progress_callback or _noop_progress

    # --- Step 1: Ingest ---
    logger.info("Step 1: Ingesting data for cycle %d from %s", cycle_year, data_dir)
    cb("ingestion", 0)

    df = build_unified_dataset(
        years=[cycle_year],
        exclude_zero_scores=False,
        data_dir=data_dir,
        file_map=file_map,
    )
    applicant_count = len(df)
    logger.info("Ingested %d applicants", applicant_count)
    cb("ingestion", 10)

    # --- Step 2: Clean ---
    logger.info("Step 2: Cleaning data")
    cb("cleaning", 10)
    df = clean_dataset(df)
    cb("cleaning", 40)

    # --- Step 3: Features ---
    logger.info("Step 3: Extracting features")
    cb("features", 40)

    structured = extract_structured_features(df)
    engineered = engineer_composite_features(df)
    binary_flags = extract_binary_flags(df)

    # Load rubric scores if available
    rubric_df = None
    rpath = rubric_scores_path or (CACHE_DIR / "rubric_scores.json")
    if rpath.exists():
        rubric_df = load_rubric_features(rpath)
        if rubric_df.empty:
            rubric_df = None
            logger.info("Rubric scores empty, proceeding without them")
        else:
            logger.info("Loaded rubric scores for %d applicants", len(rubric_df))

    if rubric_df is not None:
        features_df = combine_feature_sets(structured, engineered, binary_flags, rubric_df)
    else:
        features_df = combine_feature_sets(structured, engineered, binary_flags)

    cb("features", 60)

    # --- Step 4: ML Score ---
    logger.info("Step 4: Loading model and predicting scores")
    cb("ml_scoring", 60)

    model_path = MODELS_DIR / model_pkl
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    with open(model_path, "rb") as f:
        model_results = pickle.load(f)

    # Find the best regressor (prefer XGBoost, fallback to any regressor)
    regressor_key = None
    for key in model_results:
        if key.startswith("reg_"):
            if "XGBoost" in key or regressor_key is None:
                regressor_key = key

    if regressor_key is None:
        raise ValueError(f"No regressor found in {model_pkl}")

    model_data = model_results[regressor_key]
    model = model_data["model"]
    scaler = model_data["scaler"]

    # Build feature matrix matching the model's expected columns
    feature_cols = [
        c for c in features_df.columns
        if c != ID_COLUMN
    ]

    X = features_df[feature_cols].values.astype(float)
    X = np.nan_to_num(X, nan=0.0)
    X_scaled = scaler.transform(X)

    predicted_scores = model.predict(X_scaled)
    predicted_scores = np.clip(predicted_scores, 0, 25)

    cb("ml_scoring", 80)

    # --- Step 5: Triage ---
    logger.info("Step 5: Assigning triage tiers")
    cb("triage", 80)

    tiers = [_score_to_tier(s) for s in predicted_scores]
    tier_labels = [TIER_LABELS[t] for t in tiers]

    # Build output DataFrame
    output = df[[ID_COLUMN]].copy()
    if "app_year" in df.columns:
        output["app_year"] = df["app_year"]
    output["predicted_score"] = predicted_scores
    output["triage_tier"] = tiers
    output["triage_label"] = tier_labels

    # Save
    output_path = PROCESSED_DIR / f"master_{cycle_year}.csv"
    output.to_csv(output_path, index=False)
    logger.info("Saved %d scored applicants to %s", len(output), output_path)

    # Tier distribution
    tier_dist = {}
    for i, label in enumerate(TIER_LABELS):
        count = int((output["triage_tier"] == i).sum())
        tier_dist[label] = count

    cb("triage", 100)

    return {
        "applicant_count": applicant_count,
        "tier_distribution": tier_dist,
        "output_path": str(output_path),
        "model_used": model_pkl,
        "regressor": regressor_key,
    }
