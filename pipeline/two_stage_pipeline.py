"""Two-stage screening pipeline: Safety Gate + Quality Ranker.

Orchestrates training, inference, and evaluation of the two-stage model
that selects candidates for human review with minimal contamination.
"""

import logging
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, recall_score, roc_auc_score

from pipeline.config import (
    LOW_SCORE_THRESHOLD,
    MODELS_DIR,
    PROCESSED_DIR,
    PRODUCTION_K,
    PRODUCTION_POOL_SIZE,
    RANDOM_STATE,
    TRAIN_YEARS,
    TEST_YEAR,
)
from pipeline.model_training import (
    train_safety_gate,
    train_quality_ranker,
    compute_shap_values,
)
from pipeline.model_evaluation import (
    evaluate_two_stage,
    bootstrap_evaluate,
    majority_class_baseline,
    binary_baseline,
    single_feature_baselines,
    screening_gain,
)

logger = logging.getLogger(__name__)


# -- Inference ---------------------------------------------------------------


def triage_applicants(
    X_pool: np.ndarray,
    gate: Any,
    ranker: Any,
    gate_threshold: float,
    n_select: int = PRODUCTION_K,
) -> dict[str, Any]:
    """Run two-stage triage on a pool of applicants.

    Args:
        gate: CalibratedClassifierCV (prefit sigmoid).
        ranker: XGBRegressor (quantile alpha=0.25).
        gate_threshold: float from threshold sweep.
        n_select: number of candidates to select for human review.
    """
    # Stage 1: Safety gate
    p_low = gate.predict_proba(X_pool)[:, 1]
    passed_gate = p_low < gate_threshold
    n_passed = int(passed_gate.sum())

    if n_passed < n_select:
        logger.warning(
            "Only %d passed gate (need %d). Consider relaxing threshold.", n_passed, n_select,
        )

    # Stage 2: Rank safe candidates
    if n_passed == 0:
        logger.error("No candidates passed the gate.")
        return {
            "selected_indices": np.array([], dtype=int),
            "predicted_scores": np.array([]),
            "p_low": np.array([]),
            "gate_rejection_rate": 1.0,
            "n_passed_gate": 0,
        }

    X_safe = X_pool[passed_gate]
    predicted_scores = ranker.predict(X_safe)

    # Select top n_select by predicted score
    n_take = min(n_select, len(predicted_scores))
    ranking = np.argsort(predicted_scores)[::-1][:n_take]

    passed_indices = np.where(passed_gate)[0]

    return {
        "selected_indices": passed_indices[ranking],
        "predicted_scores": predicted_scores[ranking],
        "p_low": p_low[passed_gate][ranking],
        "gate_rejection_rate": 1 - (n_passed / len(X_pool)),
        "n_passed_gate": n_passed,
    }


# -- End-to-end training + evaluation ---------------------------------------


def run_baselines(split: dict) -> dict:
    """Phase 0: Run baseline sanity checks and return baseline metrics."""
    y_test_score = split["y_test_score"]
    y_test_bucket = split["y_test_bucket"]

    # Majority class baselines
    bucket_baseline = majority_class_baseline(y_test_bucket)
    binary_bl = binary_baseline(y_test_score, LOW_SCORE_THRESHOLD)

    # Single feature baselines
    y_test_binary = (y_test_score <= LOW_SCORE_THRESHOLD).astype(int)
    feat_baselines = single_feature_baselines(
        split["X_test"], y_test_binary, split["feature_names"], top_k=5,
    )

    results = {
        "bucket_majority_class": bucket_baseline,
        "binary_baseline": binary_bl,
        "top_features_by_auc": feat_baselines,
    }

    logger.info("Baseline — 4-bucket majority acc: %.3f", bucket_baseline["accuracy"])
    logger.info("Baseline — binary low/high split: %d low / %d high (%.1f%%)",
                binary_bl["n_low"], binary_bl["n_high"], binary_bl["low_pct"] * 100)
    for feat in feat_baselines:
        logger.info("  %s: AUC=%.3f", feat["feature"], feat["auc"])

    return results


def train_two_stage(split: dict) -> dict[str, Any]:
    """Train the complete two-stage pipeline and evaluate on test set.

    Returns dict with trained artifacts, metrics, and evaluation results.
    """
    X_train = split["X_train"]
    X_test = split["X_test"]
    y_train_score = split["y_train_score"]
    y_test_score = split["y_test_score"]
    feature_names = split["feature_names"]

    # Binary targets
    y_test_binary = (y_test_score <= LOW_SCORE_THRESHOLD).astype(int)

    # --- Phase 0: Baselines ---
    logger.info("=== Phase 0: Baselines ===")
    baselines = run_baselines(split)

    # --- Phase 2: Train Safety Gate ---
    logger.info("=== Phase 2: Safety Gate ===")
    gate_result = train_safety_gate(X_train, y_train_score)

    calibrated_gate = gate_result["calibrated_gate"]
    threshold = gate_result["threshold"]

    # Evaluate gate on test set
    p_low_test = calibrated_gate.predict_proba(X_test)[:, 1]
    gate_pred = (p_low_test >= threshold).astype(int)
    gate_recall = float(recall_score(y_test_binary, gate_pred, zero_division=0))
    gate_auc = float(roc_auc_score(y_test_binary, p_low_test))
    gate_gain = float(screening_gain(y_test_binary, gate_pred))
    gate_rejection_rate = float(gate_pred.mean())

    logger.info(
        "Gate test: recall=%.3f, AUC=%.3f, gain=%.1f, rejection_rate=%.3f",
        gate_recall, gate_auc, gate_gain, gate_rejection_rate,
    )

    # --- Phase 3: Train Quality Ranker ---
    logger.info("=== Phase 3: Quality Ranker ===")
    ranker_result = train_quality_ranker(X_train, y_train_score)
    ranker_model = ranker_result["ranker_model"]

    # Evaluate ranker on test set (high-scoring subset)
    high_test_mask = y_test_score > LOW_SCORE_THRESHOLD
    if high_test_mask.sum() > 0:
        X_test_high = X_test[high_test_mask]
        y_test_high = y_test_score[high_test_mask]
        y_pred_high = ranker_model.predict(X_test_high)
        result = spearmanr(y_test_high, y_pred_high)
        ranker_spearman = float(result[0])  # type: ignore[arg-type]
        ranker_mae = float(np.mean(np.abs(y_test_high - y_pred_high)))
        logger.info("Ranker test (high only): Spearman=%.3f, MAE=%.3f", ranker_spearman, ranker_mae)
    else:
        ranker_spearman = 0.0
        ranker_mae = float("inf")

    # --- Phase 4: Combined triage ---
    logger.info("=== Phase 4: Combined Triage ===")
    predictions = triage_applicants(
        X_test, calibrated_gate, ranker_model, threshold,
        n_select=PRODUCTION_K,
    )

    # Evaluate with proportional K
    two_stage_metrics = evaluate_two_stage(
        y_test_score, predictions,
        low_threshold=LOW_SCORE_THRESHOLD,
        production_pool_size=PRODUCTION_POOL_SIZE,
        production_k=PRODUCTION_K,
    )

    # Bootstrap CIs
    logger.info("Computing bootstrap CIs (1000 resamples)...")
    bootstrap_cis = bootstrap_evaluate(
        y_test_score, predictions, n_bootstrap=1000,
        low_threshold=LOW_SCORE_THRESHOLD,
        production_pool_size=PRODUCTION_POOL_SIZE,
        production_k=PRODUCTION_K,
    )

    logger.info("Two-stage results:")
    logger.info("  Contamination rate: %.3f", two_stage_metrics["contamination_rate"])
    logger.info("  Precision@K: %.3f", two_stage_metrics["precision_at_k"])
    logger.info("  Mean score selected: %.1f", two_stage_metrics["mean_score_selected"])
    logger.info("  Min score selected: %.1f", two_stage_metrics["min_score_selected"])
    logger.info("  Gate rejection rate: %.3f", two_stage_metrics["gate_rejection_rate"])

    # SHAP for gate and ranker
    logger.info("Computing SHAP values...")
    gate_shap = compute_shap_values(
        gate_result["gate_model"], X_test, feature_names, model_type="tree",
    )
    ranker_shap = compute_shap_values(
        ranker_model, X_test, feature_names, model_type="tree",
    )

    # Package results
    results = {
        "baselines": baselines,
        "gate": {
            "model": gate_result["gate_model"],
            "calibrated": calibrated_gate,
            "threshold": threshold,
            "test_recall": gate_recall,
            "test_auc": gate_auc,
            "test_gain": gate_gain,
            "rejection_rate": gate_rejection_rate,
        },
        "ranker": {
            "model": ranker_model,
            "test_spearman": ranker_spearman,
            "test_mae": ranker_mae,
            "n_train": ranker_result["n_train"],
        },
        "two_stage_metrics": two_stage_metrics,
        "bootstrap_cis": bootstrap_cis,
        "predictions": predictions,
        "gate_shap": gate_shap,
        "ranker_shap": ranker_shap,
        "feature_names": feature_names,
    }

    return results


def save_two_stage_artifacts(results: dict) -> None:
    """Save two-stage model artifacts via joblib."""
    artifacts = {
        "gate": results["gate"]["calibrated"],
        "ranker": results["ranker"]["model"],
        "threshold": results["gate"]["threshold"],
        "feature_columns": results["feature_names"],
        "training_metadata": {
            "train_years": TRAIN_YEARS,
            "test_year": TEST_YEAR,
            "low_score_threshold": LOW_SCORE_THRESHOLD,
            "gate_recall": results["gate"]["test_recall"],
            "gate_auc": results["gate"]["test_auc"],
            "ranker_spearman": results["ranker"]["test_spearman"],
        },
    }
    path = MODELS_DIR / "two_stage_v1.joblib"
    joblib.dump(artifacts, path)
    logger.info("Saved two-stage artifacts to %s", path)


# -- Regression-only pipeline ------------------------------------------------


def train_regression_only(split: dict, label: str) -> dict[str, Any]:
    """Train a simple regression model, rank by predicted score, select top K.

    Returns a result dict compatible with train_two_stage() output so that
    evaluate_two_stage() and bootstrap_evaluate() work unchanged.
    """
    X_train = split["X_train"]
    X_test = split["X_test"]
    y_train_score = split["y_train_score"]
    y_test_score = split["y_test_score"]
    feature_names = split["feature_names"]
    n_test = len(X_test)

    logger.info("=== Regression-Only: %s (%d features) ===", label, len(feature_names))

    # Train GradientBoostingRegressor on ALL training data (no gate split)
    reg = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.1, random_state=RANDOM_STATE,
    )
    reg.fit(X_train, y_train_score)
    y_pred = reg.predict(X_test)

    reg_r2 = float(r2_score(y_test_score, y_pred))
    logger.info("Regression R²: %.3f", reg_r2)

    # Proportional K (same logic as evaluate_two_stage)
    k = max(1, int(PRODUCTION_K * n_test / PRODUCTION_POOL_SIZE))

    # Rank by predicted score descending, select top K
    ranking = np.argsort(y_pred)[::-1]
    selected = ranking[:k]

    # Build predictions dict compatible with evaluate_two_stage
    predictions = {
        "selected_indices": selected,
        "predicted_scores": y_pred[selected],
        "gate_rejection_rate": 0.0,
        "n_passed_gate": n_test,
    }

    # Evaluate
    two_stage_metrics = evaluate_two_stage(
        y_test_score, predictions,
        low_threshold=LOW_SCORE_THRESHOLD,
        production_pool_size=PRODUCTION_POOL_SIZE,
        production_k=PRODUCTION_K,
    )

    # Bootstrap CIs
    logger.info("Computing bootstrap CIs for %s...", label)
    bootstrap_cis = bootstrap_evaluate(
        y_test_score, predictions, n_bootstrap=1000,
        low_threshold=LOW_SCORE_THRESHOLD,
        production_pool_size=PRODUCTION_POOL_SIZE,
        production_k=PRODUCTION_K,
    )

    logger.info("  Contamination: %.3f, Precision@K: %.3f, Coverage: %.3f",
                two_stage_metrics["contamination_rate"],
                two_stage_metrics["precision_at_k"],
                two_stage_metrics["coverage"])

    # SHAP
    logger.info("Computing SHAP values for %s...", label)
    ranker_shap = compute_shap_values(reg, X_test, feature_names, model_type="tree")

    return {
        "two_stage_metrics": two_stage_metrics,
        "bootstrap_cis": bootstrap_cis,
        "predictions": predictions,
        "ranker_shap": ranker_shap,
        "feature_names": feature_names,
        "regression_r2": reg_r2,
    }


# -- Architecture bakeoff helpers --------------------------------------------


def build_bakeoff_table(results_dict: dict[str, dict]) -> pd.DataFrame:
    """Build a comparison DataFrame from all architecture results.

    Args:
        results_dict: {label: results} from train_two_stage / train_regression_only.
    """
    rows = []
    for label, res in results_dict.items():
        m = res["two_stage_metrics"]
        ci = res.get("bootstrap_cis", {})
        row = {
            "architecture": label,
            "contamination_rate": m["contamination_rate"],
            "precision_at_k": m["precision_at_k"],
            "mean_score_selected": m["mean_score_selected"],
            "min_score_selected": m["min_score_selected"],
            "coverage": m["coverage"],
            "gate_rejection_rate": m["gate_rejection_rate"],
            "k": m["k"],
            "n_test": m["n_test"],
        }
        # Add bootstrap CI bounds for key metrics
        for key in ("contamination_rate", "precision_at_k", "coverage"):
            if key in ci:
                _, lo, hi = ci[key]
                row[f"{key}_ci_lo"] = lo
                row[f"{key}_ci_hi"] = hi
        rows.append(row)

    return pd.DataFrame(rows)


def build_shap_comparison(results_dict: dict[str, dict], top_n: int = 5) -> pd.DataFrame:
    """Extract top-N features by mean |SHAP| for each architecture."""
    rows = []
    for label, res in results_dict.items():
        shap_vals = res.get("ranker_shap")
        if shap_vals is None:
            continue
        feature_names = res["feature_names"]
        # Mean absolute SHAP value per feature
        mean_abs = np.abs(shap_vals.values).mean(axis=0)
        top_idx = np.argsort(mean_abs)[::-1][:top_n]
        for rank, idx in enumerate(top_idx, 1):
            rows.append({
                "architecture": label,
                "rank": rank,
                "feature": feature_names[idx],
                "mean_abs_shap": float(mean_abs[idx]),
            })
    return pd.DataFrame(rows)


def save_bakeoff_report(table_df: pd.DataFrame, shap_df: pd.DataFrame) -> None:
    """Save architecture bakeoff and SHAP comparison CSVs."""
    table_path = PROCESSED_DIR / "architecture_bakeoff.csv"
    shap_path = PROCESSED_DIR / "shap_comparison.csv"
    table_df.to_csv(table_path, index=False)
    shap_df.to_csv(shap_path, index=False)
    logger.info("Saved architecture bakeoff to %s", table_path)
    logger.info("Saved SHAP comparison to %s", shap_path)


def save_two_stage_report(results: dict) -> None:
    """Save evaluation report as CSV."""
    metrics = results["two_stage_metrics"]
    gate = results["gate"]
    ranker = results["ranker"]

    rows = [
        {"metric": "gate_recall", "value": gate["test_recall"]},
        {"metric": "gate_auc", "value": gate["test_auc"]},
        {"metric": "gate_rejection_rate", "value": gate["rejection_rate"]},
        {"metric": "gate_threshold", "value": gate["threshold"]},
        {"metric": "ranker_spearman", "value": ranker["test_spearman"]},
        {"metric": "ranker_mae", "value": ranker["test_mae"]},
        {"metric": "contamination_rate", "value": metrics["contamination_rate"]},
        {"metric": "precision_at_k", "value": metrics["precision_at_k"]},
        {"metric": "mean_score_selected", "value": metrics["mean_score_selected"]},
        {"metric": "min_score_selected", "value": metrics["min_score_selected"]},
        {"metric": "k", "value": metrics["k"]},
    ]

    # Add bootstrap CIs
    for key, (_, lo, hi) in results.get("bootstrap_cis", {}).items():
        rows.append({"metric": f"{key}_ci_lo", "value": lo})
        rows.append({"metric": f"{key}_ci_hi", "value": hi})

    df = pd.DataFrame(rows)
    path = PROCESSED_DIR / "two_stage_report.csv"
    df.to_csv(path, index=False)
    logger.info("Saved two-stage report to %s", path)
