"""Prediction service: run models, compute SHAP, build ranked tables."""

import logging

import numpy as np
import pandas as pd
import shap

from api.config import (
    ID_COLUMN,
    TARGET_SCORE,
    BUCKET_MAP,
    STRUCTURED_FEATURES,
    ENGINEERED_FEATURES,
    EXPERIENCE_BINARY_FLAGS,
    TIER_LABELS,
    TIER_COLORS,
    SCORE_BUCKET_THRESHOLDS,
    prettify,
    score_to_tier,
)
from api.services.data_service import DataStore

logger = logging.getLogger(__name__)


def get_feature_columns(config_name: str, store: DataStore) -> list[str]:
    """Return feature columns for a given config."""
    base = STRUCTURED_FEATURES + ENGINEERED_FEATURES + EXPERIENCE_BINARY_FLAGS
    if config_name == "D_Struct+Rubric" and not store.rubric_features.empty:
        rubric_cols = [c for c in store.rubric_features.columns if c != ID_COLUMN]
        # Deduplicate: only add rubric columns not already in base
        base_set = set(base)
        extra = [c for c in rubric_cols if c not in base_set]
        return base + extra
    return base


def get_test_predictions(config_name: str, store: DataStore) -> dict | None:
    """Compute predictions for the 2024 test set."""
    results = store.model_results.get(config_name)
    if results is None:
        return None

    df = store.master_data.copy()
    if df.empty:
        return None

    # Merge rubric features for Plan B
    if config_name == "D_Struct+Rubric" and not store.rubric_features.empty:
        df = df.merge(store.rubric_features, on=ID_COLUMN, how="left", suffixes=("", "_rub"))
        df = df.drop(columns=[c for c in df.columns if c.endswith("_rub")])

    feature_cols = get_feature_columns(config_name, store)

    valid = df["bucket_label"].notna()
    df_valid = df[valid].copy().reset_index(drop=True)

    year_col = "Appl_Year" if "Appl_Year" in df_valid.columns else "app_year"
    test_mask = df_valid[year_col] == 2024

    for col in feature_cols:
        if col not in df_valid.columns:
            df_valid[col] = 0.0

    X_test = df_valid.loc[test_mask, feature_cols].values.astype(float)
    X_test = np.nan_to_num(X_test, nan=0.0)
    if X_test.shape[0] == 0:
        return None

    y_test_bucket = df_valid.loc[test_mask, "bucket_label"].values.astype(int)
    y_test_score = df_valid.loc[test_mask, TARGET_SCORE].values.astype(float)
    test_ids = df_valid.loc[test_mask, ID_COLUMN].values

    clf_key = next((k for k in ["clf_XGBoost", "clf_LogisticRegression"] if k in results), None)
    reg_key = next((k for k in ["reg_XGBoost", "reg_Ridge"] if k in results), None)
    if clf_key is None or reg_key is None:
        return None

    scaler = results[clf_key]["scaler"]
    X_scaled = scaler.transform(X_test)
    clf_pred = results[clf_key]["model"].predict(X_scaled)
    clf_proba = (
        results[clf_key]["model"].predict_proba(X_scaled)
        if hasattr(results[clf_key]["model"], "predict_proba")
        else None
    )
    reg_pred = np.clip(results[reg_key]["model"].predict(X_scaled), 0, 25)

    return {
        "clf_pred": clf_pred,
        "clf_proba": clf_proba,
        "reg_pred": reg_pred,
        "y_true_bucket": y_test_bucket,
        "y_true_score": y_test_score,
        "test_ids": test_ids,
        "feature_cols": feature_cols,
        "X_test": X_test,
        "X_scaled": X_scaled,
        "clf_key": clf_key,
        "reg_key": reg_key,
        "n_classes": clf_proba.shape[1] if clf_proba is not None else 4,
    }


def build_prediction_table(config_name: str, store: DataStore) -> list[dict]:
    """Build a ranked table with predictions, tiers, and confidence."""
    preds = get_test_predictions(config_name, store)
    if preds is None:
        return []

    rows = []
    for i in range(len(preds["test_ids"])):
        amcas_id = int(preds["test_ids"][i])
        reg_score = float(preds["reg_pred"][i])
        clf_bucket = int(preds["clf_pred"][i])
        reg_tier = score_to_tier(reg_score)
        clf_reg_agree = clf_bucket == reg_tier

        confidence = 0.5
        if preds["clf_proba"] is not None:
            confidence = float(np.max(preds["clf_proba"][i]))

        tier = reg_tier
        rows.append({
            "amcas_id": amcas_id,
            "predicted_score": round(reg_score, 2),
            "predicted_bucket": clf_bucket,
            "tier": tier,
            "tier_label": TIER_LABELS[tier],
            "tier_color": TIER_COLORS[tier],
            "confidence": round(confidence, 3),
            "clf_reg_agree": clf_reg_agree,
            "actual_score": float(preds["y_true_score"][i]),
            "actual_bucket": int(preds["y_true_bucket"][i]),
            "app_year": 2024,
        })

    rows.sort(key=lambda r: r["predicted_score"], reverse=True)
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank

    return rows


def compute_shap_for_applicant(
    config_name: str,
    amcas_id: int,
    store: DataStore,
    top_n: int = 5,
) -> list[dict]:
    """Compute SHAP values for a single applicant."""
    preds = get_test_predictions(config_name, store)
    if preds is None:
        return []

    idx = None
    for i, tid in enumerate(preds["test_ids"]):
        if int(tid) == amcas_id:
            idx = i
            break
    if idx is None:
        return []

    results = store.model_results[config_name]
    reg_key = preds["reg_key"]
    model = results[reg_key]["model"]

    try:
        explainer = shap.TreeExplainer(model)
        sv = explainer(preds["X_scaled"])
        values = sv.values[idx]
    except Exception:
        background = shap.sample(preds["X_scaled"], min(100, len(preds["X_scaled"])))
        explainer = shap.Explainer(model.predict, background)
        sv = explainer(preds["X_scaled"][idx:idx+1])
        values = sv.values[0]

    feature_names = preds["feature_cols"]
    pairs = list(zip(feature_names, values))
    pairs.sort(key=lambda x: abs(x[1]), reverse=True)

    drivers = []
    for feat, val in pairs[:top_n]:
        drivers.append({
            "feature": feat,
            "display_name": prettify(feat),
            "value": round(float(val), 4),
            "direction": "positive" if val > 0 else "negative",
        })
    return drivers
