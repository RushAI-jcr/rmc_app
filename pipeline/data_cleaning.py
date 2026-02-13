"""Data cleaning: drop high-missingness columns, impute remaining NaN, audit trail."""

import logging

import pandas as pd
import numpy as np

from pipeline.config import COLUMNS_TO_DROP, ID_COLUMN

logger = logging.getLogger(__name__)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Apply centralized cleaning to the unified dataset.

    Steps:
        1. Drop columns with >70% missingness (defined in COLUMNS_TO_DROP).
        2. Fix Disadvantanged_Ind typo -> Disadvantaged_Ind.
        3. Impute experience hours and financial percentages as 0.
        4. Impute Age with median if any missing.
        5. Log all transformations for audit trail.
    """
    df = df.copy()

    # Step 1: Drop high-missingness columns
    dropped = []
    for col in COLUMNS_TO_DROP:
        if col in df.columns:
            pct_missing = df[col].isna().mean() * 100
            df = df.drop(columns=[col])
            dropped.append((col, pct_missing))

    for col, pct in dropped:
        logger.info("Dropped column %-35s (%.1f%% missing)", col, pct)
    logger.info("Dropped %d high-missingness columns", len(dropped))

    # Step 2: Fix typo in Disadvantanged_Ind
    if "Disadvantanged_Ind" in df.columns and "Disadvantaged_Ind" not in df.columns:
        df = df.rename(columns={"Disadvantanged_Ind": "Disadvantaged_Ind"})
        logger.info("Fixed typo: Disadvantanged_Ind -> Disadvantaged_Ind")

    # Step 3: Impute experience hours as 0
    hour_cols = [c for c in df.columns if "Hour" in c or "Hours" in c]
    for col in hour_cols:
        n_filled = df[col].isna().sum()
        if n_filled > 0:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            logger.info("Imputed %d NaN -> 0 in %s", n_filled, col)

    # Step 4: Impute financial percentages as 0
    pct_cols = [c for c in df.columns if "Pct" in c or "Percent" in c]
    for col in pct_cols:
        n_filled = df[col].isna().sum()
        if n_filled > 0:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            logger.info("Imputed %d NaN -> 0 in %s", n_filled, col)

    # Step 5: Impute Age with median
    if "Age" in df.columns:
        n_missing_age = df["Age"].isna().sum()
        if n_missing_age > 0:
            median_age = df["Age"].median()
            df["Age"] = df["Age"].fillna(median_age)
            logger.info("Imputed %d missing Age values with median %.1f", n_missing_age, median_age)

    # Audit summary
    remaining_cols = [c for c in df.columns if c != ID_COLUMN]
    remaining_missing = {c: df[c].isna().mean() for c in remaining_cols if df[c].isna().any()}
    if remaining_missing:
        worst = max(remaining_missing, key=remaining_missing.get)
        logger.info(
            "Post-cleaning: %d columns with any NaN (worst: %s at %.1f%%)",
            len(remaining_missing),
            worst,
            remaining_missing[worst] * 100,
        )
    else:
        logger.info("Post-cleaning: no remaining NaN in feature columns")

    logger.info("Clean dataset: %d rows, %d columns", len(df), len(df.columns))
    return df
