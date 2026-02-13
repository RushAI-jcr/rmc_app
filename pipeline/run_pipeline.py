"""CLI entry point: python -m pipeline.run_pipeline

Runs the full ML pipeline end-to-end:
  1. Data ingestion (xlsx -> unified DataFrames)
  2. Data cleaning
  3. Feature engineering (structured + engineered + rubric)
  4. Model training (Plan A: structured, Plan B: structured + rubric)
  5. Model evaluation (bakeoff comparison)
  6. Fairness audit
  7. Two-stage screening model (--two-stage flag)
  8. Gate fairness audit (runs with --two-stage)
"""

import argparse
import logging
import time

import pandas as pd

from pipeline.config import (
    ID_COLUMN,
    TARGET_SCORE,
    STRUCTURED_FEATURES,
    ENGINEERED_FEATURES,
    EXPERIENCE_BINARY_FLAGS,
    PROCESSED_DIR,
)
from pipeline.data_ingestion import build_unified_dataset, save_master_csvs
from pipeline.data_cleaning import clean_dataset
from pipeline.feature_engineering import (
    extract_structured_features,
    engineer_composite_features,
    extract_binary_flags,
    load_rubric_features,
    combine_feature_sets,
    get_feature_columns,
)
from pipeline.model_training import temporal_split, train_and_evaluate
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


def run(skip_ingestion: bool = False, skip_rubric: bool = False, two_stage: bool = False, bakeoff: bool = False) -> None:
    t0 = time.time()

    # Step 1: Data ingestion
    if skip_ingestion:
        logger.info("Skipping ingestion, loading from processed CSVs...")
        dfs = []
        for year in [2022, 2023, 2024]:
            p = PROCESSED_DIR / f"master_{year}.csv"
            if p.exists():
                dfs.append(pd.read_csv(p))
        df = pd.concat(dfs, ignore_index=True)
        logger.info("Loaded %d rows from existing CSVs", len(df))
    else:
        logger.info("=== Step 1: Data Ingestion ===")
        df = build_unified_dataset()
        save_master_csvs()
        logger.info("Ingestion complete: %d applicants, %d columns", len(df), len(df.columns))

    # Step 2: Data cleaning
    logger.info("=== Step 2: Data Cleaning ===")
    df = clean_dataset(df)

    # Step 3: Feature engineering
    logger.info("=== Step 3: Feature Engineering ===")
    structured = extract_structured_features(df)
    engineered = engineer_composite_features(df)
    binary_flags = extract_binary_flags(df)

    rubric_df = None
    if not skip_rubric:
        rubric_df = load_rubric_features()
        if rubric_df.empty:
            logger.warning("No rubric features found, proceeding without them")
            rubric_df = None

    # Target columns to merge back
    target_cols = [ID_COLUMN, TARGET_SCORE, "bucket_label", "app_year"]
    targets_df = df[[c for c in target_cols if c in df.columns]].copy()

    # Plan A: Structured + Engineered (no rubric)
    plan_a_features = combine_feature_sets(structured, engineered, binary_flags)
    plan_a_features = plan_a_features.merge(targets_df, on=ID_COLUMN, how="left")

    plan_a_feature_cols = [
        c for c in plan_a_features.columns
        if c not in {ID_COLUMN, TARGET_SCORE, "bucket_label", "app_year",
                     "Service_Rating_Categorical", "Service_Rating_Numerical"}
    ]

    # Plan B: Structured + Engineered + Rubric
    plan_b_features = None
    plan_b_feature_cols = None
    if rubric_df is not None:
        plan_b_features = combine_feature_sets(structured, engineered, binary_flags, rubric_df)
        plan_b_features = plan_b_features.merge(targets_df, on=ID_COLUMN, how="inner")
        plan_b_feature_cols = [
            c for c in plan_b_features.columns
            if c not in {ID_COLUMN, TARGET_SCORE, "bucket_label", "app_year",
                         "Service_Rating_Categorical", "Service_Rating_Numerical"}
        ]

    # Step 4: Model training
    logger.info("=== Step 4: Model Training ===")
    all_results = {}

    logger.info("--- Plan A: Structured Only (%d features) ---", len(plan_a_feature_cols))
    split_a = temporal_split(plan_a_features, plan_a_feature_cols)
    results_a = train_and_evaluate(split_a)
    save_model_results(results_a, "A_Structured")
    all_results["A_Structured"] = results_a

    split_b = None
    if plan_b_features is not None and plan_b_feature_cols is not None:
        logger.info("--- Plan B: Structured + Rubric (%d features) ---", len(plan_b_feature_cols))
        split_b = temporal_split(plan_b_features, plan_b_feature_cols)
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
    # Run fairness on Plan A XGBoost classifier
    if "clf_XGBoost" in results_a:
        scaler = results_a["clf_XGBoost"]["scaler"]
        clf = results_a["clf_XGBoost"]["model"]
        X_test_scaled = scaler.transform(split_a["X_test"])
        y_pred = clf.predict(X_test_scaled)
        y_true = split_a["y_test_bucket"]

        # Get the test portion of plan_a_features for protected attributes
        # Use the same filtering as temporal_split
        valid = plan_a_features["bucket_label"].notna()
        df_valid = plan_a_features[valid].copy()
        test_mask = df_valid["app_year"] == 2024
        test_ids = df_valid.loc[test_mask, ID_COLUMN].values

        # Get protected attributes from original df for those IDs
        test_df = df[df[ID_COLUMN].isin(test_ids)].reset_index(drop=True)
        # Reorder to match test_ids order
        test_df = test_df.set_index(ID_COLUMN).loc[test_ids].reset_index()

        fairness_df = full_fairness_audit(y_true, y_pred, test_df)
        if not fairness_df.empty:
            logger.info("\n%s", fairness_df.to_string(index=False))

    # Step 7: Two-stage screening model (optional)
    if two_stage:
        logger.info("=== Step 7: Two-Stage Screening Model ===")
        # Use Plan A split (structured features) for the two-stage model
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

        valid = plan_a_features["bucket_label"].notna()
        df_valid = plan_a_features[valid].copy()
        test_mask_ts = df_valid["app_year"] == 2024
        test_ids_ts = df_valid.loc[test_mask_ts, ID_COLUMN].values
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

        # 1. Regression-only Plan A (structured)
        bakeoff_results["Regression Only (Structured)"] = train_regression_only(
            split_a, "Regression Only (Structured)",
        )

        # 2. Regression-only Plan B (structured + rubric)
        if split_b is not None:
            bakeoff_results["Regression Only (Struct+Rubric)"] = train_regression_only(
                split_b, "Regression Only (Struct+Rubric)",
            )

        # 3. Two-stage Plan A (structured)
        logger.info("--- Two-Stage Plan A ---")
        ts_a = train_two_stage(split_a)
        bakeoff_results["Two-Stage (Structured)"] = ts_a

        # 4. Two-stage Plan B (structured + rubric)
        if split_b is not None:
            logger.info("--- Two-Stage Plan B ---")
            ts_b = train_two_stage(split_b)
            bakeoff_results["Two-Stage (Struct+Rubric)"] = ts_b

        # Build comparison tables
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
