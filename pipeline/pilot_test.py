"""Pilot test: measure whether LLM rubric scores add predictive value over Plan A.

Usage:
    python -m pipeline.pilot_test
    python -m pipeline.pilot_test --rubric-cache data/cache/rubric_scores_v2.json

Loads the 50 rubric-scored test applicants, trains Plan A on the full training set,
and runs three analyses to determine GO/NO-GO for scoring all ~2,400 applicants.

Zero API calls — uses only cached rubric scores and existing processed CSVs.
"""

import argparse
import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import LeaveOneOut, cross_val_predict

from pipeline.config import (
    ALL_RUBRIC_DIMS,
    CACHE_DIR,
    CURATED_RUBRIC_DIMS,
    ID_COLUMN,
    PROCESSED_DIR,
    TARGET_SCORE,
    TRAIN_YEARS,
    TEST_YEAR,
    FEATURE_DISPLAY_NAMES,
    score_to_tier,
)
from pipeline.feature_engineering import FeaturePipeline
from pipeline.model_training import train_and_evaluate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_from_processed_csvs() -> pd.DataFrame:
    """Load existing master CSVs (same pattern as run_pipeline.py)."""
    dfs = []
    for year in [2022, 2023, 2024]:
        p = PROCESSED_DIR / f"master_{year}.csv"
        if p.exists():
            dfs.append(pd.read_csv(p))
    df = pd.concat(dfs, ignore_index=True)
    logger.info("Loaded %d rows from existing CSVs", len(df))
    return df


def _build_split(
    feature_df: pd.DataFrame,
    targets_df: pd.DataFrame,
    feature_cols: list[str],
) -> dict:
    """Build the split dict consumed by train_and_evaluate()."""
    merged = feature_df.merge(targets_df, on=ID_COLUMN, how="inner")
    valid = merged["bucket_label"].notna()
    merged = merged[valid].copy()

    train_mask = merged["app_year"].isin(TRAIN_YEARS)
    test_mask = merged["app_year"] == TEST_YEAR

    X_train = np.nan_to_num(merged.loc[train_mask, feature_cols].values.astype(float), nan=0.0)
    X_test = np.nan_to_num(merged.loc[test_mask, feature_cols].values.astype(float), nan=0.0)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train_score": merged.loc[train_mask, TARGET_SCORE].values.astype(float),
        "y_test_score": merged.loc[test_mask, TARGET_SCORE].values.astype(float),
        "y_train_bucket": merged.loc[train_mask, "bucket_label"].values.astype(int),
        "y_test_bucket": merged.loc[test_mask, "bucket_label"].values.astype(int),
        "feature_names": feature_cols,
        "test_ids": merged.loc[test_mask, ID_COLUMN].values,
    }


def load_pilot_data(rubric_cache_path: Path) -> tuple:
    """Load CSVs, train Plan A, build aligned rubric matrix for scored test records.

    Returns:
        (split_a, results_a, rubric_matrix, actual_scores, actual_buckets,
         pilot_ids, dim_names)
    """
    # 1. Load processed data
    df = _load_from_processed_csvs()

    # 2. Temporal split + feature engineering (Plan A: no rubric)
    train_df = df[df["app_year"].isin(TRAIN_YEARS)].copy()
    test_df = df[df["app_year"] == TEST_YEAR].copy()

    target_cols = [ID_COLUMN, TARGET_SCORE, "bucket_label", "app_year"]
    targets_df = df[[c for c in target_cols if c in df.columns]].copy()

    pipe_a = FeaturePipeline(include_rubric=False)
    X_train_a = pipe_a.fit_transform(train_df)
    X_test_a = pipe_a.transform(test_df)
    feature_cols_a = pipe_a.feature_columns_

    X_all_a = pd.concat([X_train_a, X_test_a], ignore_index=True)
    split_a = _build_split(X_all_a, targets_df, feature_cols_a)

    # 3. Train Plan A models
    logger.info("Training Plan A models (%d features)...", len(feature_cols_a))
    results_a = train_and_evaluate(split_a)

    # 4. Load rubric cache (v2 format)
    with open(rubric_cache_path) as f:
        raw_cache = json.load(f)

    # Flatten v2 format: {id: {scores: {...}, ...}} -> {id: {dim: val}}
    rubric_data: dict[str, dict] = {}
    for aid, record in raw_cache.items():
        if isinstance(record, dict) and "scores" in record:
            rubric_data[aid] = record["scores"]
        else:
            rubric_data[aid] = record

    # 5. Build pilot mask and rubric matrix
    test_ids = split_a["test_ids"]
    scored_ids = set(rubric_data.keys())
    pilot_mask = np.array([str(int(tid)) in scored_ids for tid in test_ids])
    pilot_ids = test_ids[pilot_mask]

    n_pilot = int(pilot_mask.sum())
    logger.info("Pilot subset: %d of %d test records have rubric scores", n_pilot, len(test_ids))

    # Build rubric matrix aligned to ALL_RUBRIC_DIMS
    rubric_matrix = np.zeros((n_pilot, len(ALL_RUBRIC_DIMS)))
    for i, tid in enumerate(pilot_ids):
        scores = rubric_data.get(str(int(tid)), {})
        for j, dim in enumerate(ALL_RUBRIC_DIMS):
            rubric_matrix[i, j] = scores.get(dim, 0)

    actual_scores = split_a["y_test_score"][pilot_mask]
    actual_buckets = split_a["y_test_bucket"][pilot_mask]

    return (split_a, results_a, rubric_matrix, actual_scores, actual_buckets,
            pilot_ids, pilot_mask, ALL_RUBRIC_DIMS)


# ---------------------------------------------------------------------------
# Plan A predictions
# ---------------------------------------------------------------------------


def get_plan_a_predictions(
    results_a: dict, split_a: dict, pilot_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract Plan A XGBoost predictions for pilot subset."""
    scaler = results_a["reg_XGBoost"]["scaler"]
    reg = results_a["reg_XGBoost"]["model"]
    clf = results_a["clf_XGBoost"]["model"]

    X_test_scaled = scaler.transform(split_a["X_test"])
    reg_preds = np.clip(reg.predict(X_test_scaled), 0, 25)[pilot_mask]
    clf_preds = clf.predict(X_test_scaled)[pilot_mask]

    return reg_preds, clf_preds


# ---------------------------------------------------------------------------
# Analysis 1: Raw Signal
# ---------------------------------------------------------------------------


def analysis_1_raw_signal(
    rubric_matrix: np.ndarray,
    actual_scores: np.ndarray,
    dim_names: list[str],
) -> dict:
    """Do rubric scores correlate with actual applicant quality?"""
    n = len(actual_scores)
    correlations = []

    for j, dim in enumerate(dim_names):
        col = rubric_matrix[:, j]
        nonzero = col > 0
        n_nonzero = int(nonzero.sum())
        if n_nonzero < 10:
            correlations.append({
                "dim": dim, "n": n_nonzero,
                "pearson_r": np.nan, "pearson_p": np.nan,
                "spearman_r": np.nan, "spearman_p": np.nan,
            })
            continue

        pr, pp = pearsonr(col[nonzero], actual_scores[nonzero])
        sr, sp = spearmanr(col[nonzero], actual_scores[nonzero])
        correlations.append({
            "dim": dim, "n": n_nonzero,
            "pearson_r": pr, "pearson_p": pp,
            "spearman_r": sr, "spearman_p": sp,
        })

    # LOO-CV Ridge: rubric -> actual score
    loo_preds = cross_val_predict(
        Ridge(alpha=1.0), rubric_matrix, actual_scores, cv=LeaveOneOut(),
    )
    r2_loo = r2_score(actual_scores, loo_preds)
    mae_loo = mean_absolute_error(actual_scores, loo_preds)

    # Sort by absolute Pearson r
    correlations.sort(key=lambda x: abs(x["pearson_r"]) if not np.isnan(x["pearson_r"]) else 0, reverse=True)

    return {
        "correlations": correlations,
        "loo_r2": r2_loo,
        "loo_mae": mae_loo,
        "n_pilot": n,
    }


# ---------------------------------------------------------------------------
# Analysis 2: Incremental Value
# ---------------------------------------------------------------------------


def analysis_2_incremental_value(
    plan_a_preds: np.ndarray,
    actual_scores: np.ndarray,
    rubric_matrix: np.ndarray,
    dim_names: list[str],
) -> dict:
    """Do rubric scores explain what Plan A gets wrong?"""
    residuals = actual_scores - plan_a_preds
    mae_plan_a = mean_absolute_error(actual_scores, plan_a_preds)

    # Per-dimension residual correlations
    residual_correlations = []
    for j, dim in enumerate(dim_names):
        col = rubric_matrix[:, j]
        nonzero = col > 0
        n_nonzero = int(nonzero.sum())
        if n_nonzero < 10:
            residual_correlations.append({
                "dim": dim, "n": n_nonzero, "r": np.nan, "p": np.nan,
            })
            continue

        r, p = pearsonr(col[nonzero], residuals[nonzero])
        residual_correlations.append({"dim": dim, "n": n_nonzero, "r": r, "p": p})

    # LOO-CV Ridge: rubric -> residuals, then correct Plan A
    loo_residual_preds = cross_val_predict(
        Ridge(alpha=1.0), rubric_matrix, residuals, cv=LeaveOneOut(),
    )
    corrected_preds = plan_a_preds + loo_residual_preds
    mae_corrected = mean_absolute_error(actual_scores, corrected_preds)

    # Incremental R2: how much of the residual variance does rubric explain?
    ss_res_before = np.sum(residuals ** 2)
    ss_res_after = np.sum((residuals - loo_residual_preds) ** 2)
    incremental_r2 = 1 - (ss_res_after / ss_res_before) if ss_res_before > 0 else 0.0

    # Count significant dimensions
    n_significant = sum(
        1 for c in residual_correlations
        if not np.isnan(c["p"]) and c["p"] < 0.05
    )

    residual_correlations.sort(
        key=lambda x: abs(x["r"]) if not np.isnan(x["r"]) else 0, reverse=True,
    )

    return {
        "mae_plan_a": mae_plan_a,
        "mae_corrected": mae_corrected,
        "mae_delta": mae_plan_a - mae_corrected,
        "incremental_r2": incremental_r2,
        "n_significant": n_significant,
        "residual_correlations": residual_correlations,
    }


# ---------------------------------------------------------------------------
# Analysis 3: Simulated Plan B (Stacking)
# ---------------------------------------------------------------------------


def analysis_3_simulated_plan_b(
    plan_a_preds: np.ndarray,
    actual_scores: np.ndarray,
    rubric_matrix: np.ndarray,
    actual_buckets: np.ndarray,
) -> dict:
    """LOO stacking: Plan A alone vs Plan A + rubric."""
    X_a_only = plan_a_preds.reshape(-1, 1)
    X_stacked = np.column_stack([plan_a_preds, rubric_matrix])

    # LOO-CV predictions
    loo_a = cross_val_predict(Ridge(alpha=1.0), X_a_only, actual_scores, cv=LeaveOneOut())
    loo_b = cross_val_predict(Ridge(alpha=10.0), X_stacked, actual_scores, cv=LeaveOneOut())

    # Regression metrics
    mae_a = mean_absolute_error(actual_scores, loo_a)
    mae_b = mean_absolute_error(actual_scores, loo_b)
    r2_a = r2_score(actual_scores, loo_a)
    r2_b = r2_score(actual_scores, loo_b)
    rmse_a = float(np.sqrt(mean_squared_error(actual_scores, loo_a)))
    rmse_b = float(np.sqrt(mean_squared_error(actual_scores, loo_b)))

    # Classification metrics (map predictions to tiers)
    buckets_a = np.array([score_to_tier(max(0, min(25, s))) for s in loo_a])
    buckets_b = np.array([score_to_tier(max(0, min(25, s))) for s in loo_b])
    acc_a = accuracy_score(actual_buckets, buckets_a)
    acc_b = accuracy_score(actual_buckets, buckets_b)
    kappa_a = cohen_kappa_score(actual_buckets, buckets_a)
    kappa_b = cohen_kappa_score(actual_buckets, buckets_b)

    # Bootstrap 95% CI for MAE delta
    rng = np.random.default_rng(42)
    n = len(actual_scores)
    deltas = []
    for _ in range(1000):
        idx = rng.choice(n, size=n, replace=True)
        d = mean_absolute_error(actual_scores[idx], loo_a[idx]) - mean_absolute_error(actual_scores[idx], loo_b[idx])
        deltas.append(d)
    ci_lo, ci_hi = float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))

    return {
        "mae_a": mae_a, "mae_b": mae_b,
        "r2_a": r2_a, "r2_b": r2_b,
        "rmse_a": rmse_a, "rmse_b": rmse_b,
        "acc_a": acc_a, "acc_b": acc_b,
        "kappa_a": kappa_a, "kappa_b": kappa_b,
        "mae_delta": mae_a - mae_b,
        "ci_lo": ci_lo, "ci_hi": ci_hi,
    }


# ---------------------------------------------------------------------------
# Analysis 4: Feature Selection Sweep
# ---------------------------------------------------------------------------


def analysis_4_feature_selection(
    plan_a_preds: np.ndarray,
    actual_scores: np.ndarray,
    rubric_matrix: np.ndarray,
    actual_buckets: np.ndarray,
    dim_names: list[str],
) -> dict:
    """Sweep feature counts (k=1..21) to find optimal rubric subset.

    Ranks dimensions by absolute residual correlation, then tests each k
    using LOO-CV stacking (Plan A + top-k rubric dims).
    """
    residuals = actual_scores - plan_a_preds
    n = len(actual_scores)

    # Rank dims by absolute residual correlation
    dim_rankings = []
    for j in range(len(dim_names)):
        col = rubric_matrix[:, j]
        nonzero = col > 0
        if nonzero.sum() < 5:
            dim_rankings.append((j, 0.0))
            continue
        r, _ = pearsonr(col[nonzero], residuals[nonzero])
        dim_rankings.append((j, abs(r)))
    dim_rankings.sort(key=lambda x: x[1], reverse=True)

    # Baseline: Plan A only
    X_a_only = plan_a_preds.reshape(-1, 1)
    loo_a = cross_val_predict(Ridge(alpha=1.0), X_a_only, actual_scores, cv=LeaveOneOut())
    mae_baseline = mean_absolute_error(actual_scores, loo_a)
    r2_baseline = r2_score(actual_scores, loo_a)
    bkt_a = np.array([score_to_tier(max(0, min(25, s))) for s in loo_a])
    acc_baseline = accuracy_score(actual_buckets, bkt_a)
    kappa_baseline = cohen_kappa_score(actual_buckets, bkt_a)

    sweep_results = []
    k_values = [k for k in [1, 2, 3, 5, 7, 10, 15, 21] if k <= len(dim_names)]

    for k in k_values:
        top_k_idx = [idx for idx, _ in dim_rankings[:k]]
        rubric_k = rubric_matrix[:, top_k_idx]
        X_stacked = np.column_stack([plan_a_preds, rubric_k])

        # Adaptive regularization: more features -> stronger penalty
        alpha = max(1.0, k * 2.0)

        loo_b = cross_val_predict(Ridge(alpha=alpha), X_stacked, actual_scores, cv=LeaveOneOut())
        mae_k = mean_absolute_error(actual_scores, loo_b)
        r2_k = r2_score(actual_scores, loo_b)
        bkt_k = np.array([score_to_tier(max(0, min(25, s))) for s in loo_b])
        acc_k = accuracy_score(actual_buckets, bkt_k)
        kappa_k = cohen_kappa_score(actual_buckets, bkt_k)

        sweep_results.append({
            "k": k,
            "p_over_n": (k + 1) / n,
            "mae": mae_k,
            "r2": r2_k,
            "acc": acc_k,
            "kappa": kappa_k,
            "mae_delta": mae_baseline - mae_k,
            "dim_indices": top_k_idx,
        })

    # Find optimal k: maximize R2 (best continuous prediction)
    best_by_r2 = max(sweep_results, key=lambda x: x["r2"])
    best_k = best_by_r2["k"]
    best_dims = [dim_names[idx] for idx, _ in dim_rankings[:best_k]]

    # Evaluate curated 7-dim set (domain expertise + statistical signal)
    dim_list = list(dim_names)
    curated_idx = [dim_list.index(d) for d in CURATED_RUBRIC_DIMS if d in dim_list]
    curated_result = None
    if curated_idx:
        k_cur = len(curated_idx)
        rubric_cur = rubric_matrix[:, curated_idx]
        X_cur = np.column_stack([plan_a_preds, rubric_cur])
        alpha_cur = max(1.0, k_cur * 2.0)
        loo_cur = cross_val_predict(Ridge(alpha=alpha_cur), X_cur, actual_scores, cv=LeaveOneOut())
        mae_cur = mean_absolute_error(actual_scores, loo_cur)
        r2_cur = r2_score(actual_scores, loo_cur)
        bkt_cur = np.array([score_to_tier(max(0, min(25, s))) for s in loo_cur])
        acc_cur = accuracy_score(actual_buckets, bkt_cur)
        kappa_cur = cohen_kappa_score(actual_buckets, bkt_cur)
        curated_result = {
            "k": k_cur,
            "p_over_n": (k_cur + 1) / n,
            "mae": mae_cur,
            "r2": r2_cur,
            "acc": acc_cur,
            "kappa": kappa_cur,
            "mae_delta": mae_baseline - mae_cur,
            "dims": [dim_names[i] for i in curated_idx],
        }

    return {
        "baseline": {
            "mae": mae_baseline, "r2": r2_baseline,
            "acc": acc_baseline, "kappa": kappa_baseline,
        },
        "sweep": sweep_results,
        "best_k": best_k,
        "best_dims": best_dims,
        "dim_rankings": [(dim_names[idx], corr) for idx, corr in dim_rankings],
        "curated": curated_result,
    }


# ---------------------------------------------------------------------------
# Cost estimate
# ---------------------------------------------------------------------------


def estimate_costs(
    rubric_cache: dict,
    total_applicants: int,
    calls_per_applicant: int = 21,
    cost_per_call: float = 0.015,
) -> dict:
    """Estimate cost and time to score remaining applicants."""
    n_scored = len(rubric_cache)
    n_remaining = total_applicants - n_scored
    remaining_calls = n_remaining * calls_per_applicant

    # Estimate time from metadata
    times = []
    for record in rubric_cache.values():
        if isinstance(record, dict) and "metadata" in record:
            t = record["metadata"].get("elapsed_seconds")
            if t:
                times.append(t)
    avg_time = float(np.mean(times)) if times else 45.0

    return {
        "n_scored": n_scored,
        "n_remaining": n_remaining,
        "remaining_calls": remaining_calls,
        "estimated_cost_lo": remaining_calls * cost_per_call * 0.8,
        "estimated_cost_hi": remaining_calls * cost_per_call * 1.2,
        "estimated_hours": (n_remaining * avg_time) / 3600,
        "avg_seconds_per_applicant": avg_time,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report(
    signal: dict,
    incremental: dict,
    stacking: dict,
    costs: dict,
    go_r2: float,
    go_mae: float,
    feature_selection: dict | None = None,
) -> str:
    """Format GO/NO-GO report."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"RMC ADMISSIONS: LLM RUBRIC PILOT TEST (n={signal['n_pilot']})")
    lines.append("=" * 60)

    # Analysis 1
    lines.append("")
    lines.append("--- Analysis 1: Raw Signal ---")
    lines.append(f"Rubric-only Ridge (LOO-CV): R2={signal['loo_r2']:.3f}, MAE={signal['loo_mae']:.2f}")
    lines.append("")
    lines.append("Top correlated dimensions (Pearson r vs actual score):")
    for i, c in enumerate(signal["correlations"][:10]):
        if np.isnan(c["pearson_r"]):
            continue
        display = FEATURE_DISPLAY_NAMES.get(c["dim"], c["dim"])
        sig = "*" if c["pearson_p"] < 0.05 else " "
        lines.append(f"  {i+1:2d}. {display:<35s} r={c['pearson_r']:+.3f} (p={c['pearson_p']:.3f}){sig}")

    # Analysis 2
    lines.append("")
    lines.append("--- Analysis 2: Incremental Value ---")
    lines.append(f"Plan A MAE on pilot subset:         {incremental['mae_plan_a']:.2f}")
    lines.append(f"Plan A + rubric correction MAE:     {incremental['mae_corrected']:.2f} (delta: {-incremental['mae_delta']:+.2f})")
    lines.append(f"Incremental R2 (rubric explains):   {incremental['incremental_r2']:.3f}")
    lines.append(f"Significant dims (p<0.05):          {incremental['n_significant']} of {len(ALL_RUBRIC_DIMS)}")
    lines.append("")
    lines.append("Top residual-correlated dimensions:")
    for i, c in enumerate(incremental["residual_correlations"][:5]):
        if np.isnan(c["r"]):
            continue
        display = FEATURE_DISPLAY_NAMES.get(c["dim"], c["dim"])
        sig = "*" if c["p"] < 0.05 else " "
        lines.append(f"  {i+1:2d}. {display:<35s} r={c['r']:+.3f} (p={c['p']:.3f}){sig}")

    # Analysis 3
    lines.append("")
    lines.append("--- Analysis 3: Simulated Plan B (LOO Stacking) ---")
    lines.append(f"{'Metric':<20s} {'Plan A only':>14s} {'Plan A + Rubric':>16s} {'Delta':>10s}")
    lines.append("-" * 62)
    lines.append(f"{'MAE':<20s} {stacking['mae_a']:>14.2f} {stacking['mae_b']:>16.2f} {stacking['mae_a']-stacking['mae_b']:>+10.2f}")
    lines.append(f"{'R2':<20s} {stacking['r2_a']:>14.3f} {stacking['r2_b']:>16.3f} {stacking['r2_b']-stacking['r2_a']:>+10.3f}")
    lines.append(f"{'RMSE':<20s} {stacking['rmse_a']:>14.2f} {stacking['rmse_b']:>16.2f} {stacking['rmse_a']-stacking['rmse_b']:>+10.2f}")
    lines.append(f"{'Bucket Accuracy':<20s} {stacking['acc_a']*100:>13.1f}% {stacking['acc_b']*100:>15.1f}% {(stacking['acc_b']-stacking['acc_a'])*100:>+9.1f}%")
    lines.append(f"{'Cohen Kappa':<20s} {stacking['kappa_a']:>14.3f} {stacking['kappa_b']:>16.3f} {stacking['kappa_b']-stacking['kappa_a']:>+10.3f}")
    lines.append("")
    lines.append(f"Bootstrap 95% CI for MAE improvement: [{stacking['ci_lo']:.2f}, {stacking['ci_hi']:.2f}]")

    # Analysis 4: Feature Selection (if available)
    if feature_selection:
        lines.append("")
        lines.append("--- Analysis 4: Feature Selection Sweep ---")
        base = feature_selection["baseline"]
        lines.append(f"{'k dims':<10s} {'p/n':>6s} {'MAE':>8s} {'R2':>8s} {'BktAcc':>8s} {'Kappa':>8s} {'MAE_d':>8s}")
        lines.append("-" * 58)
        lines.append(
            f"{'PlanA':<10s} {'---':>6s} {base['mae']:>8.2f} {base['r2']:>8.3f} "
            f"{base['acc']*100:>7.1f}% {base['kappa']:>8.3f} {'---':>8s}"
        )
        best_k = feature_selection["best_k"]
        for row in feature_selection["sweep"]:
            marker = " *" if row["k"] == best_k else ""
            lines.append(
                f"k={row['k']:<7d} {row['p_over_n']:>6.2f} {row['mae']:>8.2f} {row['r2']:>8.3f} "
                f"{row['acc']*100:>7.1f}% {row['kappa']:>8.3f} {row['mae_delta']:>+8.2f}{marker}"
            )
        lines.append("")
        lines.append(f"Optimal k={best_k} dimensions:")
        for i, dim in enumerate(feature_selection["best_dims"]):
            display = FEATURE_DISPLAY_NAMES.get(dim, dim)
            lines.append(f"  {i+1}. {display}")

        # Curated set comparison
        curated = feature_selection.get("curated")
        if curated:
            lines.append("")
            lines.append("--- Curated 7-Dim Set (Domain + Statistical) ---")
            c = curated
            lines.append(
                f"k={c['k']:<7d} {c['p_over_n']:>6.2f} {c['mae']:>8.2f} {c['r2']:>8.3f} "
                f"{c['acc']*100:>7.1f}% {c['kappa']:>8.3f} {c['mae_delta']:>+8.2f}"
            )
            lines.append("Dimensions:")
            for i, dim in enumerate(c["dims"]):
                display = FEATURE_DISPLAY_NAMES.get(dim, dim)
                lines.append(f"  {i+1}. {display}")

    # Cost estimate (use curated 7 dims if available)
    curated_k = 7 if feature_selection and feature_selection.get("curated") else 21
    curated_calls = costs["n_remaining"] * curated_k
    curated_cost_lo = curated_calls * 0.015 * 0.8
    curated_cost_hi = curated_calls * 0.015 * 1.2
    curated_time_ratio = curated_k / 21
    curated_hours = costs["estimated_hours"] * curated_time_ratio

    lines.append("")
    lines.append("--- Cost Estimate ---")
    lines.append(f"Already scored:     {costs['n_scored']} applicants")
    lines.append(f"Remaining to score: {costs['n_remaining']} applicants")
    if curated_k < 21:
        lines.append(f"API calls (curated): {curated_calls:,} ({curated_k} per applicant)")
        lines.append(f"Estimated cost:      ${curated_cost_lo:.0f}-${curated_cost_hi:.0f}")
        lines.append(f"Estimated time:      {curated_hours:.1f} hours ({costs['avg_seconds_per_applicant'] * curated_time_ratio:.0f}s per applicant)")
        lines.append(f"  (vs full 21 dims:  {costs['remaining_calls']:,} calls, ${costs['estimated_cost_lo']:.0f}-${costs['estimated_cost_hi']:.0f}, {costs['estimated_hours']:.1f}h)")
    else:
        lines.append(f"API calls needed:   {costs['remaining_calls']:,} ({21} per applicant)")
        lines.append(f"Estimated cost:     ${costs['estimated_cost_lo']:.0f}-${costs['estimated_cost_hi']:.0f}")
        lines.append(f"Estimated time:     {costs['estimated_hours']:.1f} hours ({costs['avg_seconds_per_applicant']:.0f}s per applicant)")

    # GO/NO-GO
    criteria_met = 0
    criteria_details = []

    # Criterion 1: Incremental R2 (raw all-dims)
    if incremental["incremental_r2"] > go_r2:
        criteria_met += 1
        criteria_details.append(f"  [PASS] Incremental R2 = {incremental['incremental_r2']:.3f} > {go_r2}")
    else:
        criteria_details.append(f"  [FAIL] Incremental R2 = {incremental['incremental_r2']:.3f} <= {go_r2}")

    # Criterion 2: MAE improvement (feature-selected if available, else all-dims)
    if feature_selection:
        best = max(feature_selection["sweep"], key=lambda x: x["mae_delta"])
        fs_mae_delta = best["mae_delta"]
        if fs_mae_delta > go_mae:
            criteria_met += 1
            criteria_details.append(
                f"  [PASS] Feature-selected MAE improvement = {fs_mae_delta:.2f} > {go_mae} (k={best['k']})"
            )
        else:
            criteria_details.append(
                f"  [FAIL] Feature-selected MAE improvement = {fs_mae_delta:.2f} <= {go_mae} (k={best['k']})"
            )
    else:
        if incremental["mae_delta"] > go_mae:
            criteria_met += 1
            criteria_details.append(f"  [PASS] MAE improvement = {incremental['mae_delta']:.2f} > {go_mae}")
        else:
            criteria_details.append(f"  [FAIL] MAE improvement = {incremental['mae_delta']:.2f} <= {go_mae}")

    # Criterion 3: Number of significant dimensions
    if incremental["n_significant"] >= 3:
        criteria_met += 1
        criteria_details.append(f"  [PASS] Significant dims = {incremental['n_significant']} >= 3")
    else:
        criteria_details.append(f"  [FAIL] Significant dims = {incremental['n_significant']} < 3")

    # Criterion 4 (bonus): Feature-selected R2 positive
    if feature_selection:
        best_r2 = max(feature_selection["sweep"], key=lambda x: x["r2"])
        if best_r2["r2"] > 0:
            criteria_met += 1
            criteria_details.append(
                f"  [PASS] Feature-selected R2 = {best_r2['r2']:.3f} > 0 (k={best_r2['k']})"
            )
        else:
            criteria_details.append(
                f"  [FAIL] Feature-selected R2 = {best_r2['r2']:.3f} <= 0 (k={best_r2['k']})"
            )
        total_criteria = 4
    else:
        total_criteria = 3

    if criteria_met >= 2:
        recommendation = "GO"
        if feature_selection and feature_selection.get("curated"):
            curated = feature_selection["curated"]
            curated_dims_str = ", ".join(
                FEATURE_DISPLAY_NAMES.get(d, d) or d for d in curated["dims"]
            )
            reason = (
                f"Rubric features show incremental value with feature selection. "
                f"Recommended: score curated {curated['k']} dims ({curated_dims_str}). "
                f"Use: python -m pipeline.run_rubric_scoring_v2 --dims curated --resume"
            )
        elif feature_selection:
            best_k = feature_selection["best_k"]
            best_dims_str = ", ".join(
                FEATURE_DISPLAY_NAMES.get(d, d) or d for d in feature_selection["best_dims"]
            )
            reason = (
                f"Rubric features show incremental value with feature selection. "
                f"Recommended: score {best_k} dims ({best_dims_str})."
            )
        else:
            reason = "Rubric features show strong incremental value. Proceed with full scoring."
    elif criteria_met == 1:
        recommendation = "INCONCLUSIVE"
        reason = "Mixed signal. Consider scoring 50 more applicants (stratified by tier) before deciding."
    else:
        recommendation = "NO-GO"
        reason = "Rubric features do not provide sufficient lift over structured features alone."

    lines.append("")
    lines.append(f"--- RECOMMENDATION: {recommendation} ---")
    lines.append(f"Criteria met: {criteria_met} of {total_criteria}")
    for detail in criteria_details:
        lines.append(detail)
    lines.append("")
    lines.append(reason)

    # Caveats
    n_pilot = signal["n_pilot"]
    lines.append("")
    lines.append("--- Caveats ---")
    lines.append(f"1. Sample size (n={n_pilot}): results have {'wide' if n_pilot < 75 else 'moderate'} confidence intervals")
    lines.append("2. All rubric scores are from test set — no Plan B training possible")
    lines.append("3. Stacking simulation is optimistic (assumes perfect rubric at test time)")
    if n_pilot < 75:
        lines.append("4. Non-stratified sample may over/under-represent some score buckets")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pilot test: does LLM rubric add value over structured features?",
    )
    parser.add_argument(
        "--rubric-cache",
        type=Path,
        default=CACHE_DIR / "rubric_scores_v2.json",
        help="Path to rubric scores JSON (default: data/cache/rubric_scores_v2.json)",
    )
    parser.add_argument(
        "--cost-per-call",
        type=float,
        default=0.015,
        help="Estimated USD per LLM API call (default: 0.015)",
    )
    parser.add_argument(
        "--go-threshold-r2",
        type=float,
        default=0.05,
        help="Minimum incremental R2 for GO (default: 0.05)",
    )
    parser.add_argument(
        "--go-threshold-mae",
        type=float,
        default=0.5,
        help="Minimum MAE improvement for GO (default: 0.5)",
    )
    args = parser.parse_args()

    t0 = time.time()

    # Load data and train Plan A
    (split_a, results_a, rubric_matrix, actual_scores, actual_buckets,
     _pilot_ids, pilot_mask, dim_names) = load_pilot_data(args.rubric_cache)

    # Get Plan A predictions for pilot subset
    reg_preds, _clf_preds = get_plan_a_predictions(results_a, split_a, pilot_mask)

    # Run analyses
    logger.info("Running Analysis 1: Raw Signal...")
    signal = analysis_1_raw_signal(rubric_matrix, actual_scores, dim_names)

    logger.info("Running Analysis 2: Incremental Value...")
    incremental = analysis_2_incremental_value(reg_preds, actual_scores, rubric_matrix, dim_names)

    logger.info("Running Analysis 3: Simulated Plan B...")
    stacking = analysis_3_simulated_plan_b(reg_preds, actual_scores, rubric_matrix, actual_buckets)

    logger.info("Running Analysis 4: Feature Selection Sweep...")
    feat_sel = analysis_4_feature_selection(reg_preds, actual_scores, rubric_matrix, actual_buckets, dim_names)
    logger.info("Optimal k=%d dims, best R2=%.3f", feat_sel["best_k"], max(r["r2"] for r in feat_sel["sweep"]))

    # Cost estimate
    with open(args.rubric_cache) as f:
        raw_cache = json.load(f)
    total_applicants = len(split_a["y_train_score"]) + len(split_a["y_test_score"])
    costs = estimate_costs(raw_cache, total_applicants, cost_per_call=args.cost_per_call)

    # Generate and display report
    report = generate_report(
        signal, incremental, stacking, costs,
        go_r2=args.go_threshold_r2, go_mae=args.go_threshold_mae,
        feature_selection=feat_sel,
    )
    print(report)

    # Save to file
    output_path = PROCESSED_DIR / "pilot_report.txt"
    with open(output_path, "w") as f:
        f.write(report)
    logger.info("Report saved to %s", output_path)

    elapsed = time.time() - t0
    logger.info("Pilot test complete in %.1f seconds", elapsed)


if __name__ == "__main__":
    main()
