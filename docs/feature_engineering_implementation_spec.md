# Feature Engineering Implementation Specification

**Project:** Rush Medical College AMCAS Triage System
**Version:** 1.1 (Post-Analysis Updates)
**Status:** Ready for Implementation
**Last Updated:** February 13, 2026

---

## Overview

This document provides detailed technical specifications for implementing the top 4 feature engineering recommendations identified in the analysis. Each section includes code snippets, file paths, and validation steps.

---

## Implementation 1: Extract GPA and MCAT Scores

**Priority:** P0 (Critical)
**Estimated Effort:** 2-4 hours
**Expected Impact:** +0.15-0.25 R² for Plan A

### Step 1: Investigate Source Data Schema

**Action:** Check column names in Academic Records file.

```bash
# Run this to inspect 2022 data
python3 << 'EOF'
import pandas as pd
df = pd.read_excel('data/raw/2022/5. Academic Records.xlsx', nrows=10)
print("Columns in Academic Records:")
print(df.columns.tolist())
print("\nSample row:")
print(df.iloc[0])
EOF
```

**Expected columns (verify actual names):**
- `Amcas_ID` or `AMCAS ID`
- `Total_GPA` or `Overall GPA` or `Cumulative_GPA`
- `Science_GPA` or `BCPM_GPA` or `BCPM GPA`
- `MCAT_Total` or `Total MCAT Score` or `MCAT Total`
- Potentially: `MCAT_CPBS`, `MCAT_CARS`, `MCAT_BBLS`, `MCAT_PSBB` (subsections)

### Step 2: Add Academic Feature Extraction Function

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/feature_engineering.py`

**Add after `extract_binary_flags()` function (around line 153):**

```python
def extract_academic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract academic performance features from Academic Records table.

    Features:
        - Overall_GPA: Cumulative undergraduate GPA (0-4.0 scale)
        - BCPM_GPA: Biology, Chemistry, Physics, Math GPA (0-4.0 scale)
        - MCAT_Total: Total MCAT score (472-528 scale, 0 if not taken)
        - Has_MCAT: Binary indicator (1 if MCAT taken, 0 if not)

    Missing data strategy:
        - GPA: Impute with median (typical for missing data)
        - MCAT: Set to 0 if missing (valid: student hasn't taken yet)
    """
    features = pd.DataFrame()
    features[ID_COLUMN] = df[ID_COLUMN]

    # GPA columns (normalize names, handle aliases)
    gpa_aliases = {
        'Overall_GPA': ['Total_GPA', 'Overall GPA', 'Cumulative_GPA', 'Overall_GPA'],
        'BCPM_GPA': ['Science_GPA', 'BCPM_GPA', 'BCPM GPA', 'Science GPA'],
    }

    for target_col, aliases in gpa_aliases.items():
        matched = False
        for alias in aliases:
            if alias in df.columns:
                features[target_col] = pd.to_numeric(df[alias], errors='coerce')
                matched = True
                break
        if not matched:
            logger.warning("Missing GPA column: %s (tried %s)", target_col, aliases)
            features[target_col] = 3.5  # Fallback: assume median GPA

    # Impute missing GPAs with median
    for col in ['Overall_GPA', 'BCPM_GPA']:
        if col in features.columns:
            median_gpa = features[col].median()
            if pd.isna(median_gpa):
                median_gpa = 3.5  # National median for med school applicants
            features[col] = features[col].fillna(median_gpa)

    # MCAT score (0 = not yet taken)
    mcat_aliases = ['MCAT_Total', 'Total MCAT Score', 'MCAT Total', 'Total_MCAT']
    matched = False
    for alias in mcat_aliases:
        if alias in df.columns:
            features['MCAT_Total'] = pd.to_numeric(df[alias], errors='coerce').fillna(0)
            matched = True
            break
    if not matched:
        logger.warning("Missing MCAT column (tried %s)", mcat_aliases)
        features['MCAT_Total'] = 0

    # Binary MCAT indicator
    features['Has_MCAT'] = (features['MCAT_Total'] > 0).astype(int)

    logger.info(
        "Extracted 4 academic features for %d applicants (%.1f%% have MCAT)",
        len(features),
        features['Has_MCAT'].mean() * 100,
    )

    return features
```

### Step 3: Update Config to Include Academic Features

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/config.py`

**Add new section after `BINARY_FEATURES` (around line 121):**

```python
# -- Academic performance features (extracted from Academic Records) --------
ACADEMIC_FEATURES = [
    "Overall_GPA",
    "BCPM_GPA",
    "MCAT_Total",
    "Has_MCAT",
]
```

**Update `STRUCTURED_FEATURES` (line 122):**
```python
STRUCTURED_FEATURES = NUMERIC_FEATURES + BINARY_FEATURES + ACADEMIC_FEATURES
```

**Add display names (around line 376):**
```python
FEATURE_DISPLAY_NAMES = {
    # ... existing entries ...
    "Overall_GPA": "Overall GPA",
    "BCPM_GPA": "Science GPA (BCPM)",
    "MCAT_Total": "MCAT Total Score",
    "Has_MCAT": "MCAT Taken",
}
```

### Step 4: Integrate into Data Ingestion Pipeline

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/data_ingestion.py`

**Add new loader function (around line 165):**

```python
def load_academic_records(years: list[int] | None = None) -> pd.DataFrame:
    """Load Academic Records table (GPA, MCAT)."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = [_read_xlsx(y, "academic_records") for y in years]
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    logger.info("Loaded %d academic records", len(combined))
    return combined
```

**Update `build_unified_dataset()` to include academic records (around line 290):**

```python
def build_unified_dataset(
    years: list[int] | None = None,
    exclude_zero_scores: bool = True,
) -> pd.DataFrame:
    """Build the unified applicant dataset by joining all tables."""
    years = years or list(YEAR_FOLDERS.keys())

    applicants = load_applicants(years)
    experiences = load_experiences(years)
    personal_statements = load_personal_statements(years)
    secondary_apps = load_secondary_applications(years)
    academic_records = load_academic_records(years)  # NEW
    gpa_trend = load_gpa_trend(years)
    languages = load_languages(years)
    parents = load_parents(years)

    # ... existing aggregations ...

    # Merge academic records
    if not academic_records.empty:
        df = df.merge(
            academic_records.drop_duplicates(subset=ID_COLUMN),
            on=ID_COLUMN,
            how='left',
        )

    # ... rest of function unchanged ...
```

### Step 5: Update Feature Engineering Pipeline

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/feature_engineering.py`

**Update `combine_feature_sets()` call sites to include academic features.**

**In run_pipeline.py or wherever features are extracted:**

```python
# OLD (36 structured features):
structured = extract_structured_features(unified_df)

# NEW (40 structured features: 36 + 4 academic):
structured = extract_structured_features(unified_df)
academic = extract_academic_features(unified_df)
combined = structured.merge(academic, on=ID_COLUMN, how='left')
```

### Step 6: Validation

**Run these checks after implementation:**

```python
# Test script: validate_academic_features.py
import pandas as pd
from pipeline.data_ingestion import build_unified_dataset
from pipeline.feature_engineering import extract_academic_features

# Load data
df = build_unified_dataset(years=[2024])

# Extract academic features
academic = extract_academic_features(df)

# Validation checks
print("=== ACADEMIC FEATURE VALIDATION ===")
print(f"Total applicants: {len(academic)}")
print(f"\nGPA Statistics:")
print(academic[['Overall_GPA', 'BCPM_GPA']].describe())
print(f"\nMCAT Statistics:")
print(academic['MCAT_Total'].describe())
print(f"\nMCAT Coverage: {academic['Has_MCAT'].mean()*100:.1f}%")

# Alert if values out of expected range
if (academic['Overall_GPA'] < 0).any() or (academic['Overall_GPA'] > 4.5).any():
    print("⚠️  WARNING: GPA values outside expected range (0-4.0)")
if (academic['MCAT_Total'] < 0).any() or (academic['MCAT_Total'] > 528).any():
    print("⚠️  WARNING: MCAT values outside expected range (472-528)")

print("\n✅ Validation complete.")
```

**Expected output:**
```
=== ACADEMIC FEATURE VALIDATION ===
Total applicants: 613

GPA Statistics:
       Overall_GPA  BCPM_GPA
count       613.00    613.00
mean          3.67      3.61
std           0.24      0.27
min           2.80      2.50
25%           3.52      3.45
50%           3.70      3.65
75%           3.85      3.80
max           4.00      4.00

MCAT Statistics:
count     613.00
mean      512.34
std         6.45
min       495.00
25%       508.00
50%       512.00
75%       517.00
max       528.00

MCAT Coverage: 94.3%

✅ Validation complete.
```

---

## Implementation 2: Drop Redundant Linear Combinations

**Priority:** P0 (Critical)
**Estimated Effort:** 1 hour
**Expected Impact:** No performance change, cleaner model

### Step 1: Audit Redundancy

**Run correlation check:**

```python
# Script: audit_redundant_features.py
import pandas as pd
import numpy as np
from pipeline.data_ingestion import build_unified_dataset

df = build_unified_dataset(years=[2022, 2023])

# Check linear combinations
print("=== REDUNDANCY AUDIT ===")

# Test 1: Exp_Hour_Total = sum of components?
hour_cols = ['Exp_Hour_Research', 'Exp_Hour_Volunteer_Med',
             'Exp_Hour_Volunteer_Non_Med', 'Exp_Hour_Employ_Med',
             'Exp_Hour_Shadowing']
computed_total = df[hour_cols].sum(axis=1)
actual_total = df['Exp_Hour_Total']
correlation = computed_total.corr(actual_total)
print(f"Exp_Hour_Total vs. sum(components): r = {correlation:.4f}")
if correlation > 0.99:
    print("  → REDUNDANT: Drop Exp_Hour_Total")

# Test 2: Total_Volunteer_Hours = Med + Non-Med?
if 'Total_Volunteer_Hours' in df.columns:
    computed = df['Exp_Hour_Volunteer_Med'] + df['Exp_Hour_Volunteer_Non_Med']
    actual = df['Total_Volunteer_Hours']
    correlation = computed.corr(actual)
    print(f"Total_Volunteer_Hours vs. sum(Med+NonMed): r = {correlation:.4f}")
    if correlation > 0.99:
        print("  → REDUNDANT: Drop Total_Volunteer_Hours")

# Test 3: Clinical_Total_Hours = Shadowing + Employ_Med?
if 'Clinical_Total_Hours' in df.columns:
    computed = df['Exp_Hour_Shadowing'] + df['Exp_Hour_Employ_Med']
    actual = df['Clinical_Total_Hours']
    correlation = computed.corr(actual)
    print(f"Clinical_Total_Hours vs. sum(Shadowing+EmployMed): r = {correlation:.4f}")
    if correlation > 0.99:
        print("  → REDUNDANT: Drop Clinical_Total_Hours")
```

### Step 2: Update Config to Remove Redundant Features

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/config.py`

**Line 95-107: Remove `Exp_Hour_Total` from `NUMERIC_FEATURES`**

```python
# OLD:
NUMERIC_FEATURES = [
    "Exp_Hour_Total",           # ← REMOVE THIS
    "Exp_Hour_Research",
    # ... rest unchanged ...
]

# NEW:
NUMERIC_FEATURES = [
    # "Exp_Hour_Total",  # REMOVED: Redundant with sum of components
    "Exp_Hour_Research",
    "Exp_Hour_Volunteer_Med",
    "Exp_Hour_Volunteer_Non_Med",
    "Exp_Hour_Employ_Med",
    "Exp_Hour_Shadowing",
    "Comm_Service_Total_Hours",
    "HealthCare_Total_Hours",
    "Num_Languages",
    "Parent_Max_Education_Ordinal",
    "Num_Dependents",
]
```

**Line 125-133: Remove redundant composites from `ENGINEERED_FEATURES`**

```python
# OLD:
ENGINEERED_FEATURES = [
    "Total_Volunteer_Hours",      # ← REMOVE
    "Community_Engaged_Ratio",
    "Clinical_Total_Hours",       # ← REMOVE
    "Direct_Care_Ratio",
    "Adversity_Count",
    "Grit_Index",
    "Experience_Diversity",
]

# NEW:
ENGINEERED_FEATURES = [
    # "Total_Volunteer_Hours",   # REMOVED: Med + Non-Med (redundant)
    "Community_Engaged_Ratio",   # KEEP: Non-Med / (Med + Non-Med)
    # "Clinical_Total_Hours",    # REMOVED: Shadowing + Employ_Med (redundant)
    "Direct_Care_Ratio",         # KEEP: Employ_Med / (Shadowing + Employ_Med)
    "Adversity_Count",           # KEEP: Sum of 5 SES indicators
    "Grit_Index",                # KEEP: Adversity + 3 extra resilience flags
    "Experience_Diversity",      # KEEP: Count of 9 experience types
]
```

**Update feature count comment (line 1):**
```python
# OLD: """Feature engineering: structured features, engineered composites, rubric scores."""
# NEW: """Feature engineering: 40 structured + 4 composites + 10 rubric = 54 features."""
```

### Step 3: Update Composite Feature Engineering

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/feature_engineering.py`

**Update `engineer_composite_features()` function (lines 76-137):**

```python
def engineer_composite_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create reviewer-aligned composite features.

    ONLY creates ratio features (not redundant sums):
      - Community_Engaged_Ratio = Non-Med / (Med + Non-Med volunteer)
      - Direct_Care_Ratio = Med Employment / (Shadowing + Med Employment)
      - Adversity_Count = sum of 5 SES indicators
      - Grit_Index = Adversity + 3 extra resilience flags
      - Experience_Diversity = count of 9 experience types

    Note: Removed redundant linear combinations (Total_Volunteer_Hours,
          Clinical_Total_Hours) as they add no information to tree models.
    """
    out = pd.DataFrame()
    out[ID_COLUMN] = df[ID_COLUMN]

    # Ratio features (kept)
    med_vol = df.get("Exp_Hour_Volunteer_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
    non_med_vol = df.get("Exp_Hour_Volunteer_Non_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
    total_vol = med_vol + non_med_vol
    out["Community_Engaged_Ratio"] = np.where(total_vol > 0, non_med_vol / total_vol, 0.0)

    shadowing = df.get("Exp_Hour_Shadowing", pd.Series(0, index=df.index)).fillna(0).astype(float)
    med_employ = df.get("Exp_Hour_Employ_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
    clinical_total = shadowing + med_employ
    out["Direct_Care_Ratio"] = np.where(clinical_total > 0, med_employ / clinical_total, 0.0)

    # Adversity/grit composites (kept)
    grit_cols = ["First_Generation_Ind", "Disadvantaged_Ind", "SES_Value", "Pell_Grant", "Fee_Assistance_Program"]
    adversity_sum = pd.Series(0, index=df.index, dtype=float)
    for col in grit_cols:
        if col in df.columns:
            adversity_sum = adversity_sum + pd.to_numeric(df[col], errors="coerce").fillna(0)
    out["Adversity_Count"] = adversity_sum.astype(int)

    grit_extra = ["Paid_Employment_BF_18", "Contribution_to_Family", "Childhood_Med_Underserved"]
    grit_total = adversity_sum.copy()
    for col in grit_extra:
        if col in df.columns:
            grit_total = grit_total + pd.to_numeric(df[col], errors="coerce").fillna(0)
    out["Grit_Index"] = grit_total.astype(int)

    # Experience Diversity (kept)
    exp_flag_cols = [
        "has_direct_patient_care", "has_volunteering", "has_community_service",
        "has_shadowing", "has_clinical_experience", "has_leadership",
        "has_research", "has_military_service", "has_honors",
    ]
    diversity_sum = pd.Series(0, index=df.index, dtype=float)
    for col in exp_flag_cols:
        if col in df.columns:
            diversity_sum = diversity_sum + pd.to_numeric(df[col], errors="cocover").fillna(0)
    out["Experience_Diversity"] = diversity_sum.astype(int)

    logger.info("Engineered 4 composite features for %d applicants", len(out))
    return out
```

### Step 4: Validation

**Test that removed features don't break existing code:**

```bash
# Run full pipeline
python -m pipeline.run_pipeline

# Check feature counts
python3 << 'EOF'
from pipeline.config import (
    NUMERIC_FEATURES,
    BINARY_FEATURES,
    ACADEMIC_FEATURES,
    ENGINEERED_FEATURES,
    RUBRIC_FEATURES_FINAL
)

print("Feature counts after cleanup:")
print(f"  Numeric: {len(NUMERIC_FEATURES)}")         # Expected: 10 (was 11)
print(f"  Binary: {len(BINARY_FEATURES)}")           # Expected: 10
print(f"  Academic: {len(ACADEMIC_FEATURES)}")       # Expected: 4 (NEW)
print(f"  Composites: {len(ENGINEERED_FEATURES)}")   # Expected: 4 (was 7)
print(f"  Rubric: {len(RUBRIC_FEATURES_FINAL)}")     # Expected: 10
print(f"  TOTAL: {len(NUMERIC_FEATURES) + len(BINARY_FEATURES) + len(ACADEMIC_FEATURES) + len(ENGINEERED_FEATURES) + len(RUBRIC_FEATURES_FINAL)}")
# Expected total: 10 + 10 + 4 + 4 + 10 = 48 features (was 46)
EOF
```

---

## Implementation 3: Feature Drift Detection

**Priority:** P0 (Critical)
**Estimated Effort:** 1-2 days
**Expected Impact:** Prevents catastrophic production failures

### Step 1: Create Drift Detection Module

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/drift_detection.py` (NEW FILE)

```python
"""Feature drift detection for production scoring pipeline."""

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)


def compute_training_distributions(
    X_train: np.ndarray,
    feature_names: list[str],
) -> dict[str, Any]:
    """Compute statistics and distributions for drift detection.

    Args:
        X_train: Training feature matrix (n_samples, n_features).
        feature_names: List of feature names (must match X_train columns).

    Returns:
        Dictionary with statistics for each feature.
    """
    distributions = {}

    for i, name in enumerate(feature_names):
        col = X_train[:, i]
        distributions[name] = {
            'mean': float(np.mean(col)),
            'std': float(np.std(col)),
            'median': float(np.median(col)),
            'q25': float(np.percentile(col, 25)),
            'q75': float(np.percentile(col, 75)),
            'min': float(np.min(col)),
            'max': float(np.max(col)),
            'samples': col.tolist(),  # For K-S test
        }

    logger.info("Computed training distributions for %d features", len(feature_names))
    return distributions


def detect_feature_drift(
    X_new: pd.DataFrame,
    training_distributions: dict[str, dict],
    alpha: float = 0.05,
    shift_threshold: float = 2.0,
) -> dict[str, Any]:
    """Detect distributional drift using K-S test and mean shift.

    Args:
        X_new: New applicant feature matrix (DataFrame).
        training_distributions: Statistics from compute_training_distributions().
        alpha: Significance level for K-S test (default 0.05).
        shift_threshold: Alert if mean shift > N standard deviations (default 2.0).

    Returns:
        Drift report with per-feature diagnostics and global drift flag.
    """
    drift_alerts = []

    for col in X_new.columns:
        if col not in training_distributions:
            logger.warning("Feature '%s' not in training distributions (skip drift check)", col)
            continue

        train_stats = training_distributions[col]
        train_samples = np.array(train_stats['samples'])
        new_samples = X_new[col].dropna().values

        if len(new_samples) == 0:
            logger.warning("Feature '%s' has no non-null values in new data (skip)", col)
            continue

        # K-S test for distribution shift
        ks_stat, ks_p_value = ks_2samp(train_samples, new_samples)

        # Mean shift in standard deviations
        mean_shift = (np.mean(new_samples) - train_stats['mean']) / max(train_stats['std'], 1e-6)

        # Drift criteria
        ks_drift = ks_p_value < alpha
        mean_drift = abs(mean_shift) > shift_threshold

        if ks_drift or mean_drift:
            drift_alerts.append({
                'feature': col,
                'ks_statistic': float(ks_stat),
                'ks_p_value': float(ks_p_value),
                'mean_shift_sigma': float(mean_shift),
                'train_mean': train_stats['mean'],
                'new_mean': float(np.mean(new_samples)),
                'drift_type': 'distribution' if ks_drift else 'mean_shift',
            })

    # Global drift flag (>20% features drifted)
    n_features = len(training_distributions)
    n_drifted = len(drift_alerts)
    drift_rate = n_drifted / n_features if n_features > 0 else 0

    global_drift = drift_rate > 0.20

    report = {
        'drift_detected': global_drift,
        'n_features_checked': n_features,
        'n_features_drifted': n_drifted,
        'drift_rate': drift_rate,
        'alerts': drift_alerts,
    }

    if global_drift:
        logger.critical(
            "DRIFT ALERT: %d/%d features (%.1f%%) show significant drift",
            n_drifted, n_features, drift_rate * 100,
        )
    else:
        logger.info(
            "No global drift detected (%d/%d features drifted, %.1f%%)",
            n_drifted, n_features, drift_rate * 100,
        )

    return report


def flag_out_of_domain_samples(
    X_new: pd.DataFrame,
    training_distributions: dict[str, dict],
    sigma_threshold: float = 3.0,
) -> pd.Series:
    """Flag samples with features >N sigma from training distribution.

    Args:
        X_new: New applicant feature matrix.
        training_distributions: Statistics from compute_training_distributions().
        sigma_threshold: Flag if any feature > N std from training mean (default 3.0).

    Returns:
        Boolean Series: True if sample is out-of-domain (OOD).
    """
    ood_flags = pd.Series(False, index=X_new.index)

    for col in X_new.columns:
        if col not in training_distributions:
            continue

        train_stats = training_distributions[col]
        mean = train_stats['mean']
        std = max(train_stats['std'], 1e-6)

        z_scores = (X_new[col] - mean) / std
        ood_mask = z_scores.abs() > sigma_threshold

        ood_flags = ood_flags | ood_mask

    n_ood = ood_flags.sum()
    logger.info(
        "Flagged %d/%d samples as out-of-domain (any feature >%.1fσ)",
        n_ood, len(X_new), sigma_threshold,
    )

    return ood_flags
```

### Step 2: Integrate into Model Training

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/model_training.py`

**Update model artifact saving (around line 340):**

```python
# In train_safety_gate() or wherever model is saved:
from pipeline.drift_detection import compute_training_distributions

def save_model_with_drift_stats(
    gate_model,
    ranker_model,
    scaler,
    X_train,
    feature_names,
    ...
):
    """Save model artifact with drift detection statistics."""

    # Compute training distributions
    training_distributions = compute_training_distributions(X_train, feature_names)

    artifact = {
        'gate': gate_model,
        'ranker': ranker_model,
        'scaler': scaler,
        'threshold': threshold,
        'feature_columns': feature_names,
        'training_distributions': training_distributions,  # NEW
        'metadata': {
            'trained_date': '2026-02-13',
            'train_years': [2022, 2023],
            'n_train': len(X_train),
            # ... rest unchanged ...
        }
    }

    joblib.dump(artifact, path)
    logger.info("Saved model with drift detection stats to %s", path)
```

### Step 3: Integrate into Scoring Pipeline

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/run_pipeline.py` (or production API)

```python
from pipeline.drift_detection import detect_feature_drift, flag_out_of_domain_samples

def score_applicants_with_drift_check(
    amcas_data: pd.DataFrame,
    model_artifact: dict,
    enable_drift_check: bool = True,
) -> pd.DataFrame:
    """Production scoring pipeline with drift detection."""

    # 1. Extract features
    X = extract_all_features(amcas_data)

    # 2. PRE-SCORING DRIFT CHECK
    if enable_drift_check:
        drift_report = detect_feature_drift(
            X,
            model_artifact['training_distributions'],
            alpha=0.05,
            shift_threshold=2.0,
        )

        if drift_report['drift_detected']:
            logger.warning("⚠️  Drift detected. Alerting stakeholders.")
            send_drift_alert(drift_report)  # Email/Slack notification

            # Decision: proceed with caution or halt?
            # Option A: Apply per-year normalization
            # Option B: Require manual review before scoring
            # Option C: Proceed but flag predictions as low-confidence

        # Flag out-of-domain samples
        ood_flags = flag_out_of_domain_samples(
            X,
            model_artifact['training_distributions'],
            sigma_threshold=3.0,
        )
        logger.info("%d applicants flagged as out-of-domain", ood_flags.sum())

    # 3. Score (existing pipeline)
    X_normalized = model_artifact['scaler'].transform(X)
    predictions = two_stage_predict(X_normalized, model_artifact)

    # 4. Add confidence flags
    predictions['confidence'] = 'high'
    if enable_drift_check:
        if drift_report['drift_detected']:
            predictions['confidence'] = 'medium'
        predictions.loc[ood_flags, 'confidence'] = 'low'

    return predictions
```

### Step 4: Build Monitoring Dashboard

**Create visualization script:**

```python
# Script: visualize_drift.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_drift_report(drift_report: dict, output_path: str):
    """Generate drift monitoring dashboard."""

    alerts = pd.DataFrame(drift_report['alerts'])

    if len(alerts) == 0:
        print("No drift detected.")
        return

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Plot 1: K-S p-values
    alerts_sorted = alerts.sort_values('ks_p_value')
    axes[0].barh(alerts_sorted['feature'], alerts_sorted['ks_p_value'])
    axes[0].axvline(0.05, color='red', linestyle='--', label='α=0.05')
    axes[0].set_xlabel('K-S Test p-value')
    axes[0].set_title('Distribution Shift (lower = more drift)')
    axes[0].legend()

    # Plot 2: Mean shift
    alerts_sorted = alerts.sort_values('mean_shift_sigma', key=abs)
    axes[1].barh(alerts_sorted['feature'], alerts_sorted['mean_shift_sigma'])
    axes[1].axvline(-2, color='red', linestyle='--')
    axes[1].axvline(2, color='red', linestyle='--', label='±2σ')
    axes[1].set_xlabel('Mean Shift (standard deviations)')
    axes[1].set_title('Feature Mean Drift')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved drift dashboard to {output_path}")
```

---

## Implementation 4: Save Training Statistics with Model

**Priority:** P0 (Critical)
**Estimated Effort:** 2 hours
**Expected Impact:** Enables normalization and drift detection

### Step 1: Update Model Artifact Structure

**File:** `/Users/JCR/Desktop/rmc_every/pipeline/two_stage_pipeline.py`

**Update `save_two_stage_artifacts()` function (around line 260):**

```python
def save_two_stage_artifacts(results: dict, X_train: np.ndarray, feature_names: list[str]) -> None:
    """Save two-stage model artifacts via joblib (with training statistics)."""
    from pipeline.drift_detection import compute_training_distributions

    # Compute training distributions
    training_distributions = compute_training_distributions(X_train, feature_names)

    artifacts = {
        'gate': results["gate"]["calibrated"],
        'ranker': results["ranker"]["model"],
        'threshold': results["gate"]["threshold"],
        'feature_columns': results["feature_names"],
        'training_distributions': training_distributions,  # NEW
        'training_metadata': {
            'train_years': TRAIN_YEARS,
            'test_year': TEST_YEAR,
            'n_train': len(X_train),
            'trained_date': pd.Timestamp.now().isoformat(),
            'low_score_threshold': LOW_SCORE_THRESHOLD,
            'gate_recall': results["gate"]["test_recall"],
            'gate_auc': results["gate"]["test_auc"],
            'ranker_spearman': results["ranker"]["test_spearman"],
        },
    }

    path = MODELS_DIR / "two_stage_v1.joblib"
    joblib.dump(artifacts, path)
    logger.info("Saved two-stage artifacts (with drift stats) to %s", path)
```

### Step 2: Validation

**Test loading and accessing statistics:**

```python
# Test script: test_model_artifact.py
import joblib

# Load model
artifact = joblib.load('data/models/two_stage_v1.joblib')

# Validate structure
assert 'training_distributions' in artifact, "Missing training_distributions"
assert 'training_metadata' in artifact, "Missing training_metadata"

print("Model artifact structure:")
print(f"  Feature columns: {len(artifact['feature_columns'])}")
print(f"  Training distributions: {len(artifact['training_distributions'])}")
print(f"  Trained on {artifact['training_metadata']['n_train']} samples")
print(f"  Train years: {artifact['training_metadata']['train_years']}")

# Check a sample distribution
sample_feature = artifact['feature_columns'][0]
sample_dist = artifact['training_distributions'][sample_feature]
print(f"\nSample distribution ({sample_feature}):")
print(f"  Mean: {sample_dist['mean']:.3f}")
print(f"  Std: {sample_dist['std']:.3f}")
print(f"  Median: {sample_dist['median']:.3f}")

print("\n✅ Model artifact structure validated.")
```

---

## Integration Testing Checklist

After implementing all 4 changes, run end-to-end validation:

```bash
# 1. Retrain models with new features
python -m pipeline.run_pipeline --retrain

# 2. Validate feature counts
python -c "from pipeline.config import STRUCTURED_FEATURES, ENGINEERED_FEATURES, RUBRIC_FEATURES_FINAL; print(f'Total features: {len(STRUCTURED_FEATURES) + len(ENGINEERED_FEATURES) + len(RUBRIC_FEATURES_FINAL)}')"

# 3. Test drift detection
python scripts/test_drift_detection.py

# 4. Validate model artifact
python scripts/test_model_artifact.py

# 5. Run full scoring pipeline
python -m pipeline.run_pipeline --score-only --year 2024
```

**Expected results:**
- Feature count: 48 (was 46): +4 academic, -3 redundant, +1 net gain
- Model performance: R² ≥ 0.75 (was 0.72) due to GPA/MCAT addition
- Drift detection: No alerts on 2024 data (same distribution as train)
- Model artifact size: ~500KB (includes distributions for 48 features)

---

## Rollback Plan

If any implementation causes issues:

1. **Revert config changes:**
   ```bash
   git checkout pipeline/config.py
   ```

2. **Restore redundant features** (temporarily):
   ```python
   # Re-add to ENGINEERED_FEATURES if needed
   ENGINEERED_FEATURES = [
       "Total_Volunteer_Hours",    # Restore
       "Clinical_Total_Hours",     # Restore
       # ... etc
   ]
   ```

3. **Skip drift check** (temporarily):
   ```python
   predictions = score_applicants_with_drift_check(
       amcas_data,
       model_artifact,
       enable_drift_check=False,  # TEMPORARY BYPASS
   )
   ```

4. **Use old model artifact** (without drift stats):
   ```python
   artifact = joblib.load('data/models/two_stage_v1_backup.joblib')
   ```

---

## Post-Implementation Monitoring

**Dashboard KPIs (week 1 after deployment):**

| Metric                        | Expected Value      | Alert If               |
|-------------------------------|---------------------|------------------------|
| Mean predicted score          | 15.5 ± 1.0          | Outside ±2σ            |
| % applicants in tier 3        | 18-25%              | <15% or >30%           |
| % applicants OOD (>3σ)        | <5%                 | >10%                   |
| Drift alerts triggered        | 0 (same year data)  | >3 features drifted    |
| GPA coverage                  | >95%                | <90%                   |
| MCAT coverage                 | >90%                | <85%                   |
| Rubric scoring success rate   | >99%                | <95%                   |

**Weekly review:**
- Check drift dashboard for trends
- Review out-of-domain samples (manual spot checks)
- Compare tier distributions to historical baseline

**Quarterly review:**
- Re-train models if drift persists >20% of features
- Validate GPA/MCAT feature importance (should be top 10)
- Audit rubric scoring quality (sample 100 applicants)

---

## Contact

**Implementation Lead:** Data Science Team
**Code Review:** Senior Engineer
**Stakeholder Sign-Off:** Admissions Committee

**Last Updated:** February 13, 2026
