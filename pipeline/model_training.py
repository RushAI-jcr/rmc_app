"""ML training pipeline: classification, regression, two-stage gate/ranker, and SHAP."""

import logging
from typing import Any

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    cohen_kappa_score,
    mean_absolute_error,
    r2_score,
    classification_report,
    confusion_matrix,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from pipeline.config import (
    ID_COLUMN,
    TARGET_SCORE,
    TRAIN_YEARS,
    TEST_YEAR,
    RANDOM_STATE,
    BUCKET_LABELS,
    LOW_SCORE_THRESHOLD,
    GATE_MAX_DEPTH,
    GATE_RECALL_TARGET,
    RANKER_MAX_DEPTH,
    RANKER_QUANTILE_ALPHA,
)

logger = logging.getLogger(__name__)


# -- Data splitting ----------------------------------------------------------


def temporal_split(
    df: pd.DataFrame,
    feature_cols: list[str],
    train_years: list[int] | None = None,
    test_year: int | None = None,
) -> dict[str, Any]:
    """Split data by year: train on 2022+2023, test on 2024."""
    train_years = train_years or TRAIN_YEARS
    test_year = test_year or TEST_YEAR

    valid = df["bucket_label"].notna()
    df = df[valid].copy()

    train_mask = df["app_year"].isin(train_years)
    test_mask = df["app_year"] == test_year

    X_train = df.loc[train_mask, feature_cols].values.astype(float)
    X_test = df.loc[test_mask, feature_cols].values.astype(float)

    y_train_score = df.loc[train_mask, TARGET_SCORE].values.astype(float)
    y_test_score = df.loc[test_mask, TARGET_SCORE].values.astype(float)

    y_train_bucket = df.loc[train_mask, "bucket_label"].values.astype(int)
    y_test_bucket = df.loc[test_mask, "bucket_label"].values.astype(int)

    X_train = np.nan_to_num(X_train, nan=0.0)
    X_test = np.nan_to_num(X_test, nan=0.0)

    test_ids = df.loc[test_mask, ID_COLUMN].values

    logger.info(
        "Split: train=%d (years %s), test=%d (year %d)",
        len(X_train), train_years, len(X_test), test_year,
    )

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train_score": y_train_score,
        "y_test_score": y_test_score,
        "y_train_bucket": y_train_bucket,
        "y_test_bucket": y_test_bucket,
        "feature_names": feature_cols,
        "test_ids": test_ids,
    }


# -- Model definitions -------------------------------------------------------


def get_classifiers() -> dict[str, Any]:
    """Return dict of classifier instances to evaluate."""
    return {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, random_state=RANDOM_STATE,
        ),
        "XGBoost": GradientBoostingClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            random_state=RANDOM_STATE,
        ),
    }


def get_regressors() -> dict[str, Any]:
    """Return dict of regressor instances to evaluate."""
    return {
        "Ridge": Ridge(alpha=1.0),
        "XGBoost": GradientBoostingRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            random_state=RANDOM_STATE,
        ),
    }


# -- Training and evaluation -------------------------------------------------


def train_and_evaluate(split: dict) -> dict[str, dict]:
    """Train classifiers and regressors, return models + metrics."""
    scaler = StandardScaler()
    X_train = scaler.fit_transform(split["X_train"])
    X_test = scaler.transform(split["X_test"])

    results = {}

    # Classification (4-bucket)
    classifiers = get_classifiers()
    for name, clf in classifiers.items():
        clf.fit(X_train, split["y_train_bucket"])
        y_pred = clf.predict(X_test)

        metrics = {
            "accuracy": accuracy_score(split["y_test_bucket"], y_pred),
            "weighted_f1": f1_score(
                split["y_test_bucket"], y_pred, average="weighted", zero_division=0
            ),
            "cohen_kappa": cohen_kappa_score(split["y_test_bucket"], y_pred),
            "confusion_matrix": confusion_matrix(
                split["y_test_bucket"], y_pred
            ).tolist(),
            "classification_report": classification_report(
                split["y_test_bucket"],
                y_pred,
                target_names=BUCKET_LABELS,
                zero_division=0,
            ),
        }
        results[f"clf_{name}"] = {"model": clf, "scaler": scaler, "metrics": metrics}
        logger.info(
            "%s classification: acc=%.3f, F1=%.3f, kappa=%.3f",
            name,
            metrics["accuracy"],
            metrics["weighted_f1"],
            metrics["cohen_kappa"],
        )

    # Regression (0-25 score)
    regressors = get_regressors()
    for name, reg in regressors.items():
        reg.fit(X_train, split["y_train_score"])
        y_pred = reg.predict(X_test)

        metrics = {
            "mae": mean_absolute_error(split["y_test_score"], y_pred),
            "r2": r2_score(split["y_test_score"], y_pred),
            "rmse": float(np.sqrt(np.mean((split["y_test_score"] - y_pred) ** 2))),
        }
        results[f"reg_{name}"] = {"model": reg, "scaler": scaler, "metrics": metrics}
        logger.info(
            "%s regression: MAE=%.3f, R2=%.3f, RMSE=%.3f",
            name,
            metrics["mae"],
            metrics["r2"],
            metrics["rmse"],
        )

    return results


# -- SHAP analysis -----------------------------------------------------------


def compute_shap_values(
    model: Any,
    X: np.ndarray,
    feature_names: list[str],
    model_type: str = "tree",
) -> shap.Explanation:
    """Compute SHAP values for a trained model."""
    if model_type == "tree":
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer(X)
        except Exception:
            background = shap.sample(X, min(100, len(X)))
            explainer = shap.Explainer(model.predict, background)
            shap_values = explainer(X)
    else:
        explainer = shap.LinearExplainer(model, X)
        shap_values = explainer(X)

    return shap_values


# -- Bake-off comparison -----------------------------------------------------


def compare_models(results_dict: dict[str, dict]) -> pd.DataFrame:
    """Create a comparison table across multiple model configurations."""
    rows = []
    for config_name, models in results_dict.items():
        for model_name, model_data in models.items():
            metrics = model_data["metrics"]
            row = {
                "config": config_name,
                "model": model_name,
            }
            for k, v in metrics.items():
                if k not in ("confusion_matrix", "classification_report"):
                    row[k] = v
            rows.append(row)

    comparison = pd.DataFrame(rows)
    return comparison.sort_values(["config", "model"]).reset_index(drop=True)


# -- Two-stage: Safety Gate --------------------------------------------------


def get_safety_gate() -> xgb.XGBClassifier:
    """Return an XGBoost binary classifier configured as the safety gate."""
    n_low = 496   # approximate from training data
    n_high = 807
    scale_pos_weight = (n_high / n_low) * 2.5  # ~4.07

    return xgb.XGBClassifier(
        objective="binary:logistic",
        n_estimators=200,
        max_depth=GATE_MAX_DEPTH,
        learning_rate=0.05,
        min_child_weight=10,
        subsample=0.7,
        colsample_bytree=0.7,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        random_state=RANDOM_STATE,
    )


def train_safety_gate(
    X_train: np.ndarray,
    y_train_score: np.ndarray,
) -> dict[str, Any]:
    """Train, calibrate, and threshold-tune the safety gate.

    Uses a sequential 3-way split (60/20/20) to avoid data leakage:
      1. Train XGBoost on train_core (60%)
      2. Calibrate with CalibratedClassifierCV(cv='prefit') on calib set (20%)
      3. Sweep threshold on thresh set (20%) for >= 95% recall
    """
    # Binary target
    y_binary = (y_train_score <= LOW_SCORE_THRESHOLD).astype(int)

    # 3-way split: 60% train / 20% calibrate / 20% threshold
    X_full, X_thresh, y_full, y_thresh = train_test_split(
        X_train, y_binary, test_size=0.20, stratify=y_binary, random_state=RANDOM_STATE,
    )
    X_core, X_calib, y_core, y_calib = train_test_split(
        X_full, y_full, test_size=0.25, stratify=y_full, random_state=RANDOM_STATE,
    )
    logger.info(
        "Gate split: train_core=%d, calib=%d, thresh=%d",
        len(X_core), len(X_calib), len(X_thresh),
    )

    # Step 1: Train XGBoost
    gate_model = get_safety_gate()
    gate_model.fit(
        X_core, y_core,
        eval_set=[(X_calib, y_calib)],
        verbose=False,
    )

    # Step 2: Calibrate (FrozenEstimator wraps prefit model for sklearn >= 1.6)
    calibrated_gate = CalibratedClassifierCV(
        estimator=FrozenEstimator(gate_model),
        method="sigmoid",
    )
    calibrated_gate.fit(X_calib, y_calib)

    # Step 3: Threshold sweep on held-out thresh set
    from pipeline.model_evaluation import screening_gain

    p_low_thresh = calibrated_gate.predict_proba(X_thresh)[:, 1]
    best_threshold = None
    best_gain = float("-inf")
    best_recall = 0.0

    for t in np.arange(0.01, 0.50, 0.005):
        y_pred = (p_low_thresh >= t).astype(int)
        recall = recall_score(y_thresh, y_pred, zero_division=0)
        gain = screening_gain(y_thresh, y_pred)
        if recall >= GATE_RECALL_TARGET and gain > best_gain:
            best_threshold = float(t)
            best_recall = float(recall)
            best_gain = float(gain)

    # Fallback: if no threshold achieves target recall, use lowest tested
    if best_threshold is None:
        logger.warning(
            "No threshold achieved %.0f%% recall. Using t=0.01 as fallback.",
            GATE_RECALL_TARGET * 100,
        )
        best_threshold = 0.01
        y_pred = (p_low_thresh >= 0.01).astype(int)
        best_recall = float(recall_score(y_thresh, y_pred, zero_division=0))
        best_gain = float(screening_gain(y_thresh, y_pred))

    logger.info(
        "Gate threshold=%.3f, recall=%.3f, gain=%.1f",
        best_threshold, best_recall, best_gain,
    )

    return {
        "gate_model": gate_model,
        "calibrated_gate": calibrated_gate,
        "threshold": best_threshold,
        "threshold_recall": best_recall,
        "threshold_gain": best_gain,
    }


# -- Two-stage: Quality Ranker -----------------------------------------------


def get_quality_ranker(quantile_alpha: float | None = None) -> xgb.XGBRegressor:
    """Return an XGBoost quantile regressor configured as the quality ranker."""
    alpha = quantile_alpha or RANKER_QUANTILE_ALPHA
    return xgb.XGBRegressor(
        objective="reg:quantileerror",
        quantile_alpha=alpha,
        n_estimators=200,
        max_depth=RANKER_MAX_DEPTH,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=RANDOM_STATE,
    )


def train_quality_ranker(
    X_train: np.ndarray,
    y_train_score: np.ndarray,
    score_threshold: int | None = None,
) -> dict[str, Any]:
    """Train the quality ranker on high-scoring candidates only.

    Args:
        X_train: Feature matrix (all training samples).
        y_train_score: Continuous scores (all training samples).
        score_threshold: Only train on samples with score > threshold.
            Defaults to LOW_SCORE_THRESHOLD (15).
    """
    threshold = score_threshold if score_threshold is not None else LOW_SCORE_THRESHOLD
    high_mask = y_train_score > threshold
    X_high = X_train[high_mask]
    y_high = y_train_score[high_mask]
    logger.info("Ranker training set: %d samples (score > %d)", len(X_high), threshold)

    ranker = get_quality_ranker()
    ranker.fit(X_high, y_high, verbose=False)

    # Training set metrics
    y_pred_train = ranker.predict(X_high)
    train_mae = float(mean_absolute_error(y_high, y_pred_train))
    logger.info("Ranker train MAE: %.3f", train_mae)

    return {
        "ranker_model": ranker,
        "train_mae": train_mae,
        "n_train": len(X_high),
        "score_threshold": threshold,
    }
