"""Model evaluation: metrics computation, comparison, baselines, and two-stage metrics."""

import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from pipeline.config import MODELS_DIR, PROCESSED_DIR
from pipeline.model_training import compare_models

logger = logging.getLogger(__name__)


def save_model_results(results: dict, config_name: str) -> Path:
    """Save trained model results to a pickle file."""
    filename = f"results_{config_name}.pkl"
    path = MODELS_DIR / filename
    with open(path, "wb") as f:
        pickle.dump(results, f)
    logger.info("Saved model results to %s", path)
    return path


def load_model_results(config_name: str) -> dict | None:
    """Load trained model results from a pickle file."""
    filename = f"results_{config_name}.pkl"
    path = MODELS_DIR / filename
    if not path.exists():
        logger.warning("Model results not found: %s", path)
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def generate_bakeoff_comparison(config_results: dict[str, dict]) -> pd.DataFrame:
    """Generate and save a bakeoff comparison table.

    Args:
        config_results: {config_name: {model_key: {model, scaler, metrics}}}
    """
    comparison = compare_models(config_results)
    out_path = PROCESSED_DIR / "bakeoff_comparison.csv"
    comparison.to_csv(out_path, index=False)
    logger.info("Saved bakeoff comparison to %s", out_path)
    return comparison


def summarize_results(results: dict, config_name: str) -> dict:
    """Extract key metrics summary for a config."""
    summary = {"config": config_name}

    clf_key = next((k for k in ["clf_XGBoost", "clf_LogisticRegression"] if k in results), None)
    reg_key = next((k for k in ["reg_XGBoost", "reg_Ridge"] if k in results), None)

    if clf_key:
        m = results[clf_key]["metrics"]
        summary["best_clf"] = clf_key
        summary["accuracy"] = m["accuracy"]
        summary["weighted_f1"] = m["weighted_f1"]
        summary["cohen_kappa"] = m["cohen_kappa"]

    if reg_key:
        m = results[reg_key]["metrics"]
        summary["best_reg"] = reg_key
        summary["mae"] = m["mae"]
        summary["r2"] = m["r2"]
        summary["rmse"] = m["rmse"]

    return summary


# -- Phase 0: Baseline sanity checks ----------------------------------------


def majority_class_baseline(y_true: np.ndarray) -> dict:
    """Compute accuracy of always predicting the most common class."""
    values, counts = np.unique(y_true, return_counts=True)
    majority = values[counts.argmax()]
    acc = counts.max() / len(y_true)
    return {"majority_class": int(majority), "accuracy": float(acc), "n": len(y_true)}


def binary_baseline(y_true_score: np.ndarray, low_threshold: int = 15) -> dict:
    """Compute baseline metrics for binary low/high split."""
    is_low = (y_true_score <= low_threshold).astype(int)
    n_low = int(is_low.sum())
    n_high = int((~is_low.astype(bool)).sum())
    majority_acc = max(n_low, n_high) / len(is_low)
    return {
        "n_low": n_low,
        "n_high": n_high,
        "low_pct": n_low / len(is_low),
        "majority_class_accuracy": float(majority_acc),
    }


def single_feature_baselines(
    X: np.ndarray, y_binary: np.ndarray, feature_names: list[str], top_k: int = 5
) -> list[dict]:
    """Rank features by individual AUC for binary target, return top K."""
    from sklearn.metrics import roc_auc_score

    results = []
    for i, name in enumerate(feature_names):
        col = X[:, i]
        if np.std(col) == 0:
            continue
        try:
            auc = roc_auc_score(y_binary, col)
            auc = max(auc, 1 - auc)  # flip if negatively correlated
        except ValueError:
            continue
        results.append({"feature": name, "auc": float(auc)})

    results.sort(key=lambda r: r["auc"], reverse=True)
    return results[:top_k]


# -- Two-stage evaluation metrics --------------------------------------------


def screening_gain(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Cost matrix for is_low classification (positive class = low-scorer).

    Confusion matrix layout (sklearn):
        [[TN, FP], [FN, TP]]
    Where:
        TN = high-scorer correctly passed through      -> 0 (no cost)
        FP = high-scorer incorrectly rejected by gate  -> -1 (moderate)
        FN = low-scorer incorrectly passed through     -> -10 (catastrophic)
        TP = low-scorer correctly rejected              -> +1 (benefit)
    """
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    gain = np.array([[0, -1], [-10, +1]])
    return float(np.sum(cm * gain))


def contamination_rate(y_true_score: np.ndarray, selected_mask: np.ndarray,
                       low_threshold: int = 15) -> float:
    """Fraction of selected candidates who are actually low-scorers."""
    selected_scores = y_true_score[selected_mask]
    if len(selected_scores) == 0:
        return 0.0
    return float((selected_scores <= low_threshold).mean())


def precision_at_k(y_true_score: np.ndarray, selected_indices: np.ndarray,
                   low_threshold: int = 15) -> float:
    """Fraction of top-K selected who are actually high-scorers."""
    selected_scores = y_true_score[selected_indices]
    if len(selected_scores) == 0:
        return 0.0
    return float((selected_scores > low_threshold).mean())


def evaluate_two_stage(
    y_true_score: np.ndarray,
    predictions: dict,
    k: int | None = None,
    low_threshold: int = 15,
    production_pool_size: int = 10000,
    production_k: int = 4000,
) -> dict:
    """Evaluate two-stage model for screening quality.

    IMPORTANT: The test set has only ~519 samples, not 10K-20K.
    Scale k proportionally: k_test = production_k * (n_test / production_pool_size).
    """
    n_test = len(y_true_score)
    if k is None:
        k = max(1, int(production_k * n_test / production_pool_size))

    selected = predictions["selected_indices"][:k]

    metrics = {
        "k": k,
        "n_test": n_test,
        "contamination_rate": float((y_true_score[selected] <= low_threshold).mean()),
        "n_low_in_selected": int((y_true_score[selected] <= low_threshold).sum()),
        "precision_at_k": float((y_true_score[selected] > low_threshold).mean()),
        "mean_score_selected": float(y_true_score[selected].mean()),
        "min_score_selected": float(y_true_score[selected].min()),
        "p10_score_selected": float(np.percentile(y_true_score[selected], 10)),
        "coverage": float(
            (y_true_score[selected] > low_threshold).sum()
            / max(1, (y_true_score > low_threshold).sum())
        ),
        "gate_rejection_rate": predictions["gate_rejection_rate"],
        "n_passed_gate": predictions["n_passed_gate"],
    }
    return metrics


def bootstrap_evaluate(
    y_true_score: np.ndarray,
    predictions: dict,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    **eval_kwargs,
) -> dict[str, tuple]:
    """Bootstrap confidence intervals for all two-stage metrics."""
    rng = np.random.RandomState(42)
    all_metrics: list[dict] = []
    n = len(y_true_score)

    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        # Remap selected_indices to bootstrap sample
        boot_predictions = {
            "selected_indices": np.array([
                i for i, orig in enumerate(idx)
                if orig in set(predictions["selected_indices"])
            ]),
            "gate_rejection_rate": predictions["gate_rejection_rate"],
            "n_passed_gate": predictions["n_passed_gate"],
        }
        if len(boot_predictions["selected_indices"]) == 0:
            continue
        m = evaluate_two_stage(y_true_score[idx], boot_predictions, **eval_kwargs)
        all_metrics.append(m)

    if not all_metrics:
        return {}

    lo_pct = (1 - ci) / 2 * 100
    hi_pct = (1 + ci) / 2 * 100
    result = {}
    for key in all_metrics[0]:
        vals = [m[key] for m in all_metrics if isinstance(m[key], (int, float))]
        if vals:
            result[key] = (
                float(np.mean(vals)),
                float(np.percentile(vals, lo_pct)),
                float(np.percentile(vals, hi_pct)),
            )
    return result
