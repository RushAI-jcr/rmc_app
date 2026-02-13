"""Fairness analysis: bias detection using disparate impact and Fairlearn metrics."""

import logging

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score

from pipeline.config import DEMOGRAPHICS_FOR_FAIRNESS_ONLY, PROTECTED_ATTRIBUTES, PROCESSED_DIR

logger = logging.getLogger(__name__)


def compute_disparate_impact(
    y_pred: np.ndarray,
    sensitive_features: pd.Series,
    favorable_label: int | None = None,
) -> dict[str, float]:
    """Compute disparate impact ratio for each group vs the most-favorable group.

    DI = P(favorable | unprivileged) / P(favorable | privileged)
    A ratio >= 0.8 is typically considered acceptable (80% rule).
    """
    if favorable_label is None:
        favorable_label = max(y_pred)

    y_pred_arr = np.asarray(y_pred)
    sensitive_arr = np.asarray(sensitive_features)

    groups = pd.Series(sensitive_arr).dropna().unique()
    favorable_rates: dict[str, float] = {}

    for group in groups:
        mask = sensitive_arr == group
        group_preds = y_pred_arr[mask]
        if len(group_preds) == 0:
            continue
        favorable_rates[str(group)] = float((group_preds == favorable_label).mean())

    if not favorable_rates:
        return {}

    max_rate = max(favorable_rates.values())
    if max_rate == 0:
        return {g: 0.0 for g in favorable_rates}

    return {group: rate / max_rate for group, rate in favorable_rates.items()}


def compute_fairlearn_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: pd.Series,
) -> dict[str, float | dict | None]:
    """Compute key fairness metrics using Fairlearn."""
    from fairlearn.metrics import (
        demographic_parity_difference,
        equalized_odds_difference,
        MetricFrame,
    )

    results: dict[str, float | dict | None] = {}

    try:
        results["demographic_parity_difference"] = demographic_parity_difference(
            y_true, y_pred, sensitive_features=sensitive_features
        )
    except Exception as e:
        logger.warning("Could not compute demographic parity: %s", e)
        results["demographic_parity_difference"] = None

    try:
        results["equalized_odds_difference"] = equalized_odds_difference(
            y_true, y_pred, sensitive_features=sensitive_features
        )
    except Exception as e:
        logger.warning("Could not compute equalized odds: %s", e)
        results["equalized_odds_difference"] = None

    try:
        mf = MetricFrame(
            metrics=accuracy_score,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        results["accuracy_by_group"] = mf.by_group.to_dict()
        results["accuracy_overall"] = mf.overall
        results["accuracy_difference"] = mf.difference()
        results["accuracy_ratio"] = mf.ratio()
    except Exception as e:
        logger.warning("Could not compute accuracy by group: %s", e)

    return results


def full_fairness_audit(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    df: pd.DataFrame,
    protected_attrs: list[str] | None = None,
) -> pd.DataFrame:
    """Run a complete fairness audit across all protected attributes."""
    protected_attrs = protected_attrs or PROTECTED_ATTRIBUTES
    n = len(y_true)
    rows = []

    for attr in protected_attrs:
        if attr not in df.columns:
            logger.warning("Protected attribute %s not found in data", attr)
            continue

        raw = df[attr].iloc[:n].reset_index(drop=True)

        if attr == "Age":
            age_numeric = pd.to_numeric(raw, errors="coerce")
            sensitive = pd.cut(
                age_numeric,
                bins=[0, 25, 31, 200],
                labels=["18-24", "25-30", "31+"],
                include_lowest=True,
            ).astype(str)
            sensitive = sensitive.replace("nan", np.nan)
        else:
            sensitive = raw.copy()

        if sensitive.nunique() < 2:
            logger.warning("Skipping %s: only %d unique values", attr, sensitive.nunique())
            continue

        di = compute_disparate_impact(y_pred, sensitive)
        min_di = min(di.values()) if di else None

        valid_mask = sensitive.notna()
        if valid_mask.sum() < 10:
            continue

        fl_metrics = compute_fairlearn_metrics(
            y_true[valid_mask],
            y_pred[valid_mask],
            sensitive[valid_mask],
        )

        row = {
            "attribute": attr,
            "n_groups": sensitive.nunique(),
            "min_disparate_impact": min_di,
            "passes_80pct_rule": min_di >= 0.8 if min_di is not None else None,
            "demographic_parity_diff": fl_metrics.get("demographic_parity_difference"),
            "equalized_odds_diff": fl_metrics.get("equalized_odds_difference"),
            "accuracy_difference": fl_metrics.get("accuracy_difference"),
            "accuracy_ratio": fl_metrics.get("accuracy_ratio"),
        }
        rows.append(row)

        logger.info(
            "%s: DI=%.3f (%s), DPD=%.3f",
            attr,
            min_di or 0,
            "PASS" if row["passes_80pct_rule"] else "FAIL",
            fl_metrics.get("demographic_parity_difference", 0) or 0,
        )

    audit_df = pd.DataFrame(rows)

    if not audit_df.empty:
        out_path = PROCESSED_DIR / "fairness_report.csv"
        audit_df.to_csv(out_path, index=False)
        logger.info("Saved fairness report to %s", out_path)

    return audit_df


def audit_gate_fairness(
    p_low: np.ndarray,
    gate_threshold: float,
    y_true_score: np.ndarray,
    df: pd.DataFrame,
    low_score_threshold: int = 15,
) -> pd.DataFrame:
    """Audit safety gate for disparate rejection rates across protected groups.

    Checks whether the gate disproportionately rejects candidates from
    any demographic group. Uses DEMOGRAPHICS_FOR_FAIRNESS_ONLY (Gender,
    Age, Race, Citizenship) since these are strictly blocked from model
    features and represent pure fairness concerns.

    Args:
        p_low: Predicted probability of being a low-scorer for each candidate.
        gate_threshold: The calibrated threshold (reject if p_low >= threshold).
        y_true_score: Actual review scores for computing ground truth stats.
        df: DataFrame with protected attribute columns.
        low_score_threshold: Score at or below which a candidate is "low".

    Returns:
        DataFrame with per-attribute, per-group rejection rates and DI ratios.
    """
    gate_rejected = (p_low >= gate_threshold).astype(int)
    is_low = (y_true_score <= low_score_threshold).astype(int)
    n = len(p_low)
    rows = []

    for attr in DEMOGRAPHICS_FOR_FAIRNESS_ONLY:
        if attr not in df.columns:
            logger.warning("Gate audit: %s not found in data", attr)
            continue

        sensitive = df[attr].iloc[:n].reset_index(drop=True)

        if attr == "Age":
            age_numeric = pd.to_numeric(sensitive, errors="coerce")
            sensitive = pd.cut(
                age_numeric,
                bins=[0, 25, 31, 200],
                labels=["18-24", "25-30", "31+"],
                include_lowest=True,
            ).astype(str)
            sensitive = sensitive.replace("nan", np.nan)

        groups = sensitive.dropna().unique()
        if len(groups) < 2:
            continue

        # Per-group rejection rates
        group_rejection_rates: dict[str, float] = {}
        for group in groups:
            mask = sensitive == group
            group_rejected = gate_rejected[mask]
            if len(group_rejected) == 0:
                continue
            rejection_rate = float(group_rejected.mean())
            actual_low_rate = float(is_low[mask].mean())
            group_rejection_rates[str(group)] = rejection_rate
            rows.append({
                "attribute": attr,
                "group": str(group),
                "n": int(mask.sum()),
                "rejection_rate": rejection_rate,
                "actual_low_rate": actual_low_rate,
                "rejection_rate_minus_actual": rejection_rate - actual_low_rate,
            })

        # Compute disparate impact on rejection (lower rejection = favorable)
        if group_rejection_rates:
            min_rejection = min(group_rejection_rates.values())
            max_rejection = max(group_rejection_rates.values())
            if max_rejection > 0:
                di_ratio = min_rejection / max_rejection
            else:
                di_ratio = 1.0
            for row in rows:
                if row["attribute"] == attr:
                    row["rejection_di_ratio"] = di_ratio
                    row["passes_80pct_rule"] = di_ratio >= 0.8

    audit_df = pd.DataFrame(rows)

    if not audit_df.empty:
        out_path = PROCESSED_DIR / "gate_fairness_report.csv"
        audit_df.to_csv(out_path, index=False)
        logger.info("Saved gate fairness report to %s", out_path)

        for attr in audit_df["attribute"].unique():
            attr_df = audit_df[audit_df["attribute"] == attr]
            di = attr_df["rejection_di_ratio"].iloc[0]
            passes = attr_df["passes_80pct_rule"].iloc[0]
            logger.info(
                "Gate fairness — %s: DI=%.3f (%s)",
                attr, di, "PASS" if passes else "FAIL",
            )

    return audit_df
