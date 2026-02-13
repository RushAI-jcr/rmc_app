"""CLI entry point: python -m pipeline.run_pipeline

Runs the full ML pipeline end-to-end:
  1. Data preparation (xlsx -> unified DataFrame)
  2. Temporal split (BEFORE feature engineering to prevent leakage)
  3. Feature engineering (fit on train, transform both)
  4. Model training (Plan A: structured, Plan B: structured + rubric)
  5. Model evaluation (bakeoff comparison)
  6. Fairness audit
  7. Two-stage screening model (--two-stage flag)
  8. Gate fairness audit (runs with --two-stage)
"""

import argparse
import logging
import time

import numpy as np
import pandas as pd

from pipeline.config import (
    ID_COLUMN,
    MODELS_DIR,
    PROCESSED_DIR,
    TARGET_SCORE,
    TRAIN_YEARS,
    TEST_YEAR,
)
from pipeline.data_preparation import prepare_dataset, save_master_csvs
from pipeline.feature_engineering import FeaturePipeline
from pipeline.model_training import train_and_evaluate
from pipeline.model_evaluation import (
    save_model_results,
    generate_bakeoff_comparison,
    summarize_results,
)
from pipeline.fairness_audit import full_fairness_audit, audit_gate_fairness
from pipeline.two_stage_pipeline import (
    train_two_stage,
    train_regression_only,
    build_bakeoff_table,
    build_shap_comparison,
    save_bakeoff_report,
    save_two_stage_artifacts,
    save_two_stage_report,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _load_from_processed_csvs() -> pd.DataFrame:
    """Load existing master CSVs instead of re-ingesting."""
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
    """Build the split dict consumed by model_training.train_and_evaluate().

    Preserves the same interface as the old temporal_split() so downstream
    model training, two-stage, and fairness code work unchanged.
    """
    merged = feature_df.merge(targets_df, on=ID_COLUMN, how="inner")
    valid = merged["bucket_label"].notna()
    merged = merged[valid].copy()

    train_mask = merged["app_year"].isin(TRAIN_YEARS)
    test_mask = merged["app_year"] == TEST_YEAR

    X_train = merged.loc[train_mask, feature_cols].values.astype(float)
    X_test = merged.loc[test_mask, feature_cols].values.astype(float)

    y_train_score = merged.loc[train_mask, TARGET_SCORE].values.astype(float)
    y_test_score = merged.loc[test_mask, TARGET_SCORE].values.astype(float)

    y_train_bucket = merged.loc[train_mask, "bucket_label"].values.astype(int)
    y_test_bucket = merged.loc[test_mask, "bucket_label"].values.astype(int)

    X_train = np.nan_to_num(X_train, nan=0.0)
    X_test = np.nan_to_num(X_test, nan=0.0)

    test_ids = merged.loc[test_mask, ID_COLUMN].values

    logger.info(
        "Split: train=%d (years %s), test=%d (year %d)",
        len(X_train), TRAIN_YEARS, len(X_test), TEST_YEAR,
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


def run(
    skip_ingestion: bool = False,
    skip_rubric: bool = False,
    two_stage: bool = False,
    bakeoff: bool = False,
) -> None:
    """Full pipeline: ingest -> split -> features -> train -> evaluate -> audit."""
    t0 = time.time()

    # Step 1: Data preparation
    if skip_ingestion:
        logger.info("Skipping ingestion, loading from processed CSVs...")
        df = _load_from_processed_csvs()
    else:
        logger.info("=== Step 1: Data Preparation ===")
        df = prepare_dataset()
        save_master_csvs(df)
        logger.info("Preparation complete: %d applicants, %d columns", len(df), len(df.columns))

    # Step 2: Temporal split BEFORE feature engineering (prevents data leakage)
    logger.info("=== Step 2: Temporal Split ===")
    train_df = df[df["app_year"].isin(TRAIN_YEARS)].copy()
    test_df = df[df["app_year"] == TEST_YEAR].copy()
    logger.info("Train: %d applicants (%s), Test: %d applicants (%d)",
                len(train_df), TRAIN_YEARS, len(test_df), TEST_YEAR)

    # Preserve targets + metadata for split construction
    target_cols = [ID_COLUMN, TARGET_SCORE, "bucket_label", "app_year"]
    targets_df = df[[c for c in target_cols if c in df.columns]].copy()

    # Step 3: Feature engineering (fit on train only)
    logger.info("=== Step 3: Feature Engineering ===")

    # Plan A: Structured + Engineered (no rubric)
    pipe_a = FeaturePipeline(include_rubric=False)
    X_train_a = pipe_a.fit_transform(train_df)
    X_test_a = pipe_a.transform(test_df)
    feature_cols_a = pipe_a.feature_columns_
    pipe_a.save(MODELS_DIR / "feature_pipeline_A.joblib")

    # Combine train+test feature frames for split construction
    X_all_a = pd.concat([X_train_a, X_test_a], ignore_index=True)
    split_a = _build_split(X_all_a, targets_df, feature_cols_a)

    # Plan B: Structured + Engineered + Rubric
    split_b = None
    if not skip_rubric:
        pipe_b = FeaturePipeline(include_rubric=True)
        pipe_b.fit(train_df)
        if pipe_b._rubric_data:
            X_train_b = pipe_b.transform(train_df)
            X_test_b = pipe_b.transform(test_df)
            feature_cols_b = pipe_b.feature_columns_
            pipe_b.save(MODELS_DIR / "feature_pipeline.joblib")

            X_all_b = pd.concat([X_train_b, X_test_b], ignore_index=True)
            split_b = _build_split(X_all_b, targets_df, feature_cols_b)
        else:
            logger.warning("No rubric features found, proceeding without them")

    # Step 4: Model training
    logger.info("=== Step 4: Model Training ===")
    all_results = {}

    logger.info("--- Plan A: Structured Only (%d features) ---", len(feature_cols_a))
    results_a = train_and_evaluate(split_a)
    save_model_results(results_a, "A_Structured")
    all_results["A_Structured"] = results_a

    if split_b is not None:
        logger.info("--- Plan B: Structured + Rubric (%d features) ---", len(split_b["feature_names"]))
        results_b = train_and_evaluate(split_b)
        save_model_results(results_b, "D_Struct+Rubric")
        all_results["D_Struct+Rubric"] = results_b

    # Step 5: Model evaluation
    logger.info("=== Step 5: Model Evaluation ===")
    comparison = generate_bakeoff_comparison(all_results)
    logger.info("\n%s", comparison.to_string(index=False))

    for config_name, results in all_results.items():
        summary = summarize_results(results, config_name)
        logger.info("Summary for %s: %s", config_name, summary)

    # Step 6: Fairness audit
    logger.info("=== Step 6: Fairness Audit ===")
    if "clf_XGBoost" in results_a:
        scaler = results_a["clf_XGBoost"]["scaler"]
        clf = results_a["clf_XGBoost"]["model"]
        X_test_scaled = scaler.transform(split_a["X_test"])
        y_pred = clf.predict(X_test_scaled)
        y_true = split_a["y_test_bucket"]

        # Get protected attributes from original df for test IDs
        test_ids = split_a["test_ids"]
        test_df_audit = df[df[ID_COLUMN].isin(test_ids)].reset_index(drop=True)
        test_df_audit = test_df_audit.set_index(ID_COLUMN).loc[test_ids].reset_index()

        fairness_df = full_fairness_audit(y_true, y_pred, test_df_audit)
        if not fairness_df.empty:
            logger.info("\n%s", fairness_df.to_string(index=False))

    # Step 7: Two-stage screening model (optional)
    if two_stage:
        logger.info("=== Step 7: Two-Stage Screening Model ===")
        two_stage_results = train_two_stage(split_a)
        save_two_stage_artifacts(two_stage_results)
        save_two_stage_report(two_stage_results)

        logger.info("Two-stage summary:")
        ts_metrics = two_stage_results["two_stage_metrics"]
        logger.info("  Contamination rate: %.3f", ts_metrics["contamination_rate"])
        logger.info("  Precision@K: %.3f", ts_metrics["precision_at_k"])
        logger.info("  Gate rejection rate: %.3f", ts_metrics["gate_rejection_rate"])

        # Gate fairness audit
        logger.info("=== Step 8: Gate Fairness Audit ===")
        calibrated_gate = two_stage_results["gate"]["calibrated"]
        gate_threshold = two_stage_results["gate"]["threshold"]
        p_low_test = calibrated_gate.predict_proba(split_a["X_test"])[:, 1]

        test_ids_ts = split_a["test_ids"]
        test_df_ts = df[df[ID_COLUMN].isin(test_ids_ts)].reset_index(drop=True)
        test_df_ts = test_df_ts.set_index(ID_COLUMN).loc[test_ids_ts].reset_index()

        gate_fairness_df = audit_gate_fairness(
            p_low_test, gate_threshold, split_a["y_test_score"], test_df_ts,
        )
        if not gate_fairness_df.empty:
            logger.info("\n%s", gate_fairness_df.to_string(index=False))

    # Step 9: Architecture bakeoff (optional)
    if bakeoff:
        logger.info("=== Step 9: Architecture Bakeoff ===")
        bakeoff_results = {}

        # Regression-only Plan A
        bakeoff_results["Regression Only (Structured)"] = train_regression_only(
            split_a, "Regression Only (Structured)",
        )

        # Regression-only Plan B
        if split_b is not None:
            bakeoff_results["Regression Only (Struct+Rubric)"] = train_regression_only(
                split_b, "Regression Only (Struct+Rubric)",
            )

        # Two-stage Plan A
        logger.info("--- Two-Stage Plan A ---")
        ts_a = train_two_stage(split_a)
        bakeoff_results["Two-Stage (Structured)"] = ts_a

        # Two-stage Plan B
        if split_b is not None:
            logger.info("--- Two-Stage Plan B ---")
            ts_b = train_two_stage(split_b)
            bakeoff_results["Two-Stage (Struct+Rubric)"] = ts_b

        table_df = build_bakeoff_table(bakeoff_results)
        shap_df = build_shap_comparison(bakeoff_results)
        save_bakeoff_report(table_df, shap_df)

        logger.info("\n=== Architecture Bakeoff Results ===")
        logger.info("\n%s", table_df.to_string(index=False))
        logger.info("\n=== SHAP Top-5 Features by Architecture ===")
        logger.info("\n%s", shap_df.to_string(index=False))

    elapsed = time.time() - t0
    logger.info("=== Pipeline complete in %.1f seconds ===", elapsed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RMC admissions triage pipeline")
    parser.add_argument("--skip-ingestion", action="store_true",
                        help="Use existing processed CSVs instead of re-ingesting")
    parser.add_argument("--skip-rubric", action="store_true",
                        help="Skip rubric features (Plan A only)")
    parser.add_argument("--two-stage", action="store_true",
                        help="Run the two-stage screening model (safety gate + quality ranker)")
    parser.add_argument("--bakeoff", action="store_true",
                        help="Run 4-architecture bakeoff (regression-only vs two-stage, Plan A vs B)")
    args = parser.parse_args()
    run(skip_ingestion=args.skip_ingestion, skip_rubric=args.skip_rubric,
        two_stage=args.two_stage, bakeoff=args.bakeoff)


if __name__ == "__main__":
    main()
