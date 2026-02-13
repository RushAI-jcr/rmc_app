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
from pipeline.data_preparation import prepare_dataset
from pipeline.feature_engineering import FeaturePipeline

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
      2. Features (40%): load fitted FeaturePipeline, transform data
      3. ML Score (80%): load pre-trained model, predict scores
      4. Triage (100%): assign tiers, save output

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

    df = prepare_dataset(
        years=[cycle_year],
        data_dir=data_dir,
        file_map=file_map,
    )
    applicant_count = len(df)
    logger.info("Ingested %d applicants", applicant_count)
    cb("ingestion", 10)

    # --- Step 2: Features ---
    logger.info("Step 2: Extracting features")
    cb("features", 10)

    # Load fitted feature pipeline from training
    pipeline_path = MODELS_DIR / "feature_pipeline.joblib"
    if pipeline_path.exists():
        feature_pipe = FeaturePipeline.load(pipeline_path)
    else:
        # Fallback: try Plan A pipeline
        pipeline_a_path = MODELS_DIR / "feature_pipeline_A.joblib"
        if pipeline_a_path.exists():
            feature_pipe = FeaturePipeline.load(pipeline_a_path)
        else:
            # No saved pipeline — create one on the fly (no rubric)
            logger.warning("No saved FeaturePipeline found, creating one on the fly")
            feature_pipe = FeaturePipeline(
                include_rubric=rubric_scores_path is not None,
                rubric_path=rubric_scores_path or (CACHE_DIR / "rubric_scores.json"),
            )
            feature_pipe.fit(df)

    features_df = feature_pipe.transform(df)
    feature_cols = feature_pipe.feature_columns_

    cb("features", 40)

    # --- Step 3: ML Score ---
    logger.info("Step 3: Loading model and predicting scores")
    cb("ml_scoring", 40)

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

    X = features_df[feature_cols].values.astype(float)
    X = np.nan_to_num(X, nan=0.0)
    X_scaled = scaler.transform(X)

    predicted_scores = model.predict(X_scaled)
    predicted_scores = np.clip(predicted_scores, 0, 25)

    cb("ml_scoring", 80)

    # --- Step 4: Triage ---
    logger.info("Step 4: Assigning triage tiers")
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
