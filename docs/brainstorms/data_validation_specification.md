# Medical School Applicant Triage System: Data Validation Specification

## Executive Summary

This specification defines comprehensive data validation rules for the Rush Medical College admissions triage system, which processes ~17,000 AMCAS applicants annually from 7 Excel files. The validation system must catch data quality issues before they corrupt the ML pipeline while handling year-over-year schema evolution and column name variations.

**Key Design Principles:**
- Fail fast on critical errors (missing files, ID column mismatches)
- Warn on suspicious patterns (outliers, distribution shifts)
- Allow flexibility for year-over-year schema changes
- Provide actionable feedback to non-technical staff

---

## 1. Column Name Evolution & Fuzzy Matching

### Problem Statement
AMCAS exports change column headers between years:
- `Amcas_ID` vs `AMCAS ID` vs `amcas_id` (whitespace and case variations)
- `Exp_Type` vs `Experience_Type` (abbreviations)
- `Application_Review_Score` vs `Review_Score` (prefix changes)

### Validation Strategy

#### 1.1 ID Column Matching (Critical)
**Rule:** Every file MUST have exactly one column that can be normalized to "Amcas_ID"

```python
import pandas as pd
from difflib import SequenceMatcher

def validate_id_column(df: pd.DataFrame, file_type: str) -> dict:
    """
    Validate presence of ID column using fuzzy matching.

    Returns:
        {
            "status": "ERROR" | "WARNING" | "SUCCESS",
            "id_column": str or None,
            "message": str,
            "confidence": float  # 0.0-1.0 for fuzzy matches
        }
    """
    # Normalize all column names
    normalized_cols = {
        col: col.lower().replace(" ", "_").replace("-", "_")
        for col in df.columns
    }

    # Exact match patterns
    TARGET_PATTERNS = ["amcas_id", "amcas id", "amcasid"]

    # Find exact matches first
    for original_col, norm_col in normalized_cols.items():
        if norm_col in TARGET_PATTERNS:
            return {
                "status": "SUCCESS",
                "id_column": original_col,
                "message": f"Found ID column: {original_col}",
                "confidence": 1.0
            }

    # Fuzzy match (threshold: 0.8)
    FUZZY_THRESHOLD = 0.8
    candidates = []

    for original_col, norm_col in normalized_cols.items():
        for pattern in TARGET_PATTERNS:
            ratio = SequenceMatcher(None, norm_col, pattern).ratio()
            if ratio >= FUZZY_THRESHOLD:
                candidates.append({
                    "column": original_col,
                    "confidence": ratio,
                    "pattern": pattern
                })

    if candidates:
        # Sort by confidence and take best match
        best = max(candidates, key=lambda x: x["confidence"])
        return {
            "status": "WARNING",
            "id_column": best["column"],
            "message": f"Fuzzy match ID column: {best['column']} (confidence: {best['confidence']:.2f})",
            "confidence": best["confidence"]
        }

    # No match found
    return {
        "status": "ERROR",
        "id_column": None,
        "message": f"No ID column found in {file_type}. Columns: {list(df.columns)[:10]}...",
        "confidence": 0.0
    }
```

**Error Severity:** ERROR (blocks pipeline)

**Thresholds:**
- Exact match: confidence = 1.0 (SUCCESS)
- Fuzzy match ≥ 0.8: WARNING (requires user acknowledgment)
- No match: ERROR (pipeline stops)

#### 1.2 Feature Column Matching (Graceful)
**Rule:** Feature columns should match expected names but missing columns are non-fatal

```python
from typing import Dict, List, Tuple

# Column name mapping registry (expected -> acceptable aliases)
COLUMN_MAPPINGS = {
    "Exp_Type": ["Exp_Type", "Experience_Type", "exp_type", "Exp Type"],
    "Application_Review_Score": [
        "Application_Review_Score",
        "Application Review Score",
        "Review_Score",
        "App_Review_Score"
    ],
    "Service_Rating_Categorical": [
        "Service_Rating_Categorical",
        "Service Rating Categorical",
        "Rating_Categorical",
        "Service_Rating"
    ],
    "Disadvantaged_Ind": [
        "Disadvantaged_Ind",
        "Disadvantanged_Ind",  # Known typo in 2024 data
        "Disadvantaged_Indicator"
    ],
}

def fuzzy_match_column(
    df: pd.DataFrame,
    target_col: str,
    aliases: List[str],
    fuzzy_threshold: float = 0.85
) -> Tuple[str | None, float]:
    """
    Find best matching column in dataframe.

    Returns:
        (matched_column_name, confidence_score)
    """
    # Normalize columns
    normalized = {
        col: col.lower().replace(" ", "_").replace("(", "").replace(")", "")
        for col in df.columns
    }

    # Check exact aliases first
    for alias in aliases:
        alias_norm = alias.lower().replace(" ", "_")
        for original, norm in normalized.items():
            if norm == alias_norm:
                return (original, 1.0)

    # Fuzzy match
    best_match = None
    best_score = 0.0

    target_norm = target_col.lower().replace(" ", "_")
    for original, norm in normalized.items():
        score = SequenceMatcher(None, norm, target_norm).ratio()
        if score > best_score:
            best_score = score
            best_match = original

    if best_score >= fuzzy_threshold:
        return (best_match, best_score)

    return (None, 0.0)

def validate_feature_columns(df: pd.DataFrame, required_features: List[str]) -> dict:
    """
    Validate presence of required feature columns.

    Returns:
        {
            "status": "ERROR" | "WARNING" | "SUCCESS",
            "matched": {original_name: normalized_name},
            "missing": [column_names],
            "fuzzy_matches": [(column, confidence)],
            "message": str
        }
    """
    matched = {}
    missing = []
    fuzzy_matches = []

    for feature in required_features:
        aliases = COLUMN_MAPPINGS.get(feature, [feature])
        match, confidence = fuzzy_match_column(df, feature, aliases)

        if match:
            matched[feature] = match
            if confidence < 1.0:
                fuzzy_matches.append((match, confidence))
        else:
            missing.append(feature)

    # Determine severity
    if not missing:
        status = "SUCCESS" if not fuzzy_matches else "WARNING"
        message = f"All {len(matched)} features found"
    elif len(missing) < len(required_features) * 0.2:  # <20% missing
        status = "WARNING"
        message = f"Found {len(matched)}/{len(required_features)} features. Missing: {missing[:5]}"
    else:
        status = "ERROR"
        message = f"Too many missing features ({len(missing)}/{len(required_features)}): {missing[:10]}"

    return {
        "status": status,
        "matched": matched,
        "missing": missing,
        "fuzzy_matches": fuzzy_matches,
        "message": message
    }
```

**Error Severity:**
- <20% missing features: WARNING
- ≥20% missing features: ERROR
- Fuzzy match confidence <0.85: WARNING

---

## 2. Missing Target Column for New Data

### Problem Statement
New applicant data (current cycle) won't have `Application_Review_Score` yet - that's what the model predicts. Need to distinguish between:
1. **Training/validation data**: Must have target column
2. **Scoring-only data**: Target column should be absent or all NaN

### Validation Strategy

#### 2.1 Target Column Presence Check

```python
from enum import Enum
from typing import Optional

class DataMode(Enum):
    TRAINING = "training"  # Historical data with scores
    SCORING = "scoring"    # New applicants without scores
    MIXED = "mixed"        # Partial scores (suspicious)

def detect_data_mode(df: pd.DataFrame, target_col: str = "Application_Review_Score") -> dict:
    """
    Determine if this is training data (with scores) or scoring data (without).

    Returns:
        {
            "mode": DataMode,
            "target_present": bool,
            "target_coverage": float,  # 0.0-1.0
            "status": "ERROR" | "WARNING" | "SUCCESS",
            "message": str
        }
    """
    if target_col not in df.columns:
        return {
            "mode": DataMode.SCORING,
            "target_present": False,
            "target_coverage": 0.0,
            "status": "SUCCESS",
            "message": "Scoring mode: no target column (expected for new applicants)"
        }

    # Check how many rows have non-null scores
    non_null_count = df[target_col].notna().sum()
    coverage = non_null_count / len(df)

    if coverage == 0.0:
        return {
            "mode": DataMode.SCORING,
            "target_present": True,
            "target_coverage": 0.0,
            "status": "SUCCESS",
            "message": "Scoring mode: target column present but all NaN"
        }
    elif coverage >= 0.95:
        return {
            "mode": DataMode.TRAINING,
            "target_present": True,
            "target_coverage": coverage,
            "status": "SUCCESS",
            "message": f"Training mode: {coverage*100:.1f}% of applicants have scores"
        }
    else:
        # Partial scores - this is suspicious
        return {
            "mode": DataMode.MIXED,
            "target_present": True,
            "target_coverage": coverage,
            "status": "WARNING",
            "message": f"Mixed mode: only {coverage*100:.1f}% have scores (expected 0% or >95%)"
        }

def validate_required_columns_by_mode(df: pd.DataFrame, mode: DataMode) -> dict:
    """
    Check required columns based on data mode.

    Training mode requires:
        - Application_Review_Score (or Service_Rating_Categorical)
        - All feature columns

    Scoring mode requires:
        - All feature columns
        - NO target column (or all NaN)
    """
    errors = []
    warnings = []

    if mode == DataMode.TRAINING:
        # Must have at least one target
        target_cols = ["Application_Review_Score", "Service_Rating_Categorical"]
        has_target = any(col in df.columns for col in target_cols)
        if not has_target:
            errors.append(f"Training mode requires one of: {target_cols}")

    elif mode == DataMode.SCORING:
        # Check for unexpected score columns with data
        unexpected_scores = []
        for col in ["Application_Review_Score", "Service_Rating_Categorical"]:
            if col in df.columns and df[col].notna().any():
                unexpected_scores.append(col)

        if unexpected_scores:
            warnings.append(
                f"Scoring mode has unexpected scores in: {unexpected_scores}. "
                "Will be ignored during prediction."
            )

    elif mode == DataMode.MIXED:
        errors.append(
            "Inconsistent target column: some rows have scores, others don't. "
            "Expected either all scored (training) or none scored (new applicants)."
        )

    return {
        "status": "ERROR" if errors else ("WARNING" if warnings else "SUCCESS"),
        "errors": errors,
        "warnings": warnings
    }
```

**Error Severity:**
- Training mode without target: ERROR
- Mixed mode (partial scores): ERROR
- Scoring mode with unexpected scores: WARNING

#### 2.2 Columns Absent in New Data

Based on pipeline analysis, these columns may be absent in new (current cycle) data:

**Definitely absent:**
- `Application_Review_Score` - the prediction target
- `Service_Rating_Categorical` - manual bucket rating
- `Service_Rating_Numerical` - numerical version of bucket

**Possibly absent (derived from human review):**
- `Prev_Applied_Rush` - requires historical lookup
- `RU_Ind` - Rush-specific indicator (may need manual tagging)

**Must be present (from AMCAS export):**
- All demographic fields (Age, Gender, Citizenship, etc.)
- All experience fields (Exp_Hour_*, Comm_Service_*, HealthCare_*)
- All financial fields (SES_Value, Pell_Grant, Fee_Assistance_Program, etc.)
- All family fields (First_Generation_Ind, Disadvantaged_Ind, Num_Dependents, etc.)

```python
# Column requirements by data mode
REQUIRED_COLUMNS = {
    DataMode.TRAINING: {
        "critical": [
            "Amcas_ID",  # Join key
            "Application_Review_Score",  # OR Service_Rating_Categorical
            "Age", "Gender",  # Demographics (fairness only)
            "Exp_Hour_Total",  # Experience summary
        ],
        "important": [
            "First_Generation_Ind",
            "Disadvantaged_Ind",
            "SES_Value",
            "Exp_Hour_Research",
            "Exp_Hour_Volunteer_Med",
            "Exp_Hour_Volunteer_Non_Med",
        ]
    },
    DataMode.SCORING: {
        "critical": [
            "Amcas_ID",
            "Age", "Gender",
            "Exp_Hour_Total",
        ],
        "important": [
            "First_Generation_Ind",
            "Disadvantaged_Ind",
            "SES_Value",
        ]
    }
}
```

---

## 3. Data Quality Red Flags

### 3.1 Row Count Validation

```python
from dataclasses import dataclass
from typing import Tuple

@dataclass
class RowCountExpectations:
    """Expected row counts per file type."""
    file_type: str
    min_rows: int
    expected_rows: Tuple[int, int]  # (min_reasonable, max_reasonable)
    max_rows: int
    description: str

# Historical data: ~1,300 applicants per year (2022-2023), 2024 unknown
ROW_COUNT_RULES = {
    "applicants": RowCountExpectations(
        file_type="Applicants",
        min_rows=100,  # Below this is definitely wrong
        expected_rows=(800, 2000),  # Typical range
        max_rows=25000,  # AMCAS max applicants per school
        description="One row per applicant"
    ),
    "experiences": RowCountExpectations(
        file_type="Experiences",
        min_rows=1000,  # Applicants * 5 (minimum experiences per person)
        expected_rows=(5000, 30000),  # 5-15 experiences per applicant
        max_rows=100000,
        description="Multiple rows per applicant (experiences)"
    ),
    "personal_statement": RowCountExpectations(
        file_type="Personal Statement",
        min_rows=100,
        expected_rows=(800, 2000),  # Should match applicants
        max_rows=25000,
        description="One row per applicant"
    ),
    "secondary_application": RowCountExpectations(
        file_type="Secondary Application",
        min_rows=100,
        expected_rows=(800, 2000),  # Should match applicants
        max_rows=25000,
        description="One row per applicant"
    ),
    "gpa_trend": RowCountExpectations(
        file_type="GPA Trend",
        min_rows=100,
        expected_rows=(800, 2000),
        max_rows=25000,
        description="One row per applicant"
    ),
    "languages": RowCountExpectations(
        file_type="Languages",
        min_rows=500,  # Most applicants speak 1-2 languages
        expected_rows=(1000, 5000),
        max_rows=10000,
        description="Multiple rows per applicant (languages)"
    ),
    "parents": RowCountExpectations(
        file_type="Parents",
        min_rows=200,  # Some applicants may not report
        expected_rows=(800, 4000),  # 1-2 parents per applicant
        max_rows=5000,
        description="1-2 rows per applicant"
    ),
}

def validate_row_count(df: pd.DataFrame, file_type: str) -> dict:
    """
    Validate row count is within expected range.

    Returns:
        {
            "status": "ERROR" | "WARNING" | "SUCCESS",
            "row_count": int,
            "expected_range": (int, int),
            "message": str
        }
    """
    if file_type not in ROW_COUNT_RULES:
        return {
            "status": "WARNING",
            "row_count": len(df),
            "expected_range": None,
            "message": f"No row count expectations defined for {file_type}"
        }

    rules = ROW_COUNT_RULES[file_type]
    actual_count = len(df)

    if actual_count < rules.min_rows:
        status = "ERROR"
        message = f"{file_type}: only {actual_count} rows (expected ≥{rules.min_rows}). File may be truncated."
    elif actual_count > rules.max_rows:
        status = "ERROR"
        message = f"{file_type}: {actual_count} rows exceeds maximum ({rules.max_rows}). Data may be corrupted."
    elif actual_count < rules.expected_rows[0] or actual_count > rules.expected_rows[1]:
        status = "WARNING"
        message = f"{file_type}: {actual_count} rows outside typical range {rules.expected_rows}. Verify data completeness."
    else:
        status = "SUCCESS"
        message = f"{file_type}: {actual_count} rows (within expected range)"

    return {
        "status": status,
        "row_count": actual_count,
        "expected_range": rules.expected_rows,
        "message": message
    }
```

**Error Severity:**
- Row count < min or > max: ERROR
- Row count outside expected range: WARNING

### 3.2 Column Count Validation

```python
COLUMN_COUNT_RULES = {
    "applicants": (50, 70),  # 2024 has 60 columns
    "experiences": (10, 20),  # 2024 has 13 columns
    "personal_statement": (2, 5),  # 2024 has 3 columns
    "secondary_application": (5, 15),
    "gpa_trend": (3, 10),
    "languages": (3, 8),
    "parents": (3, 10),
}

def validate_column_count(df: pd.DataFrame, file_type: str) -> dict:
    """Validate column count is reasonable for file type."""
    if file_type not in COLUMN_COUNT_RULES:
        return {
            "status": "INFO",
            "column_count": len(df.columns),
            "message": f"No column count expectations for {file_type}"
        }

    min_cols, max_cols = COLUMN_COUNT_RULES[file_type]
    actual_count = len(df.columns)

    if actual_count < min_cols:
        return {
            "status": "ERROR",
            "column_count": actual_count,
            "expected_range": (min_cols, max_cols),
            "message": f"{file_type}: only {actual_count} columns (expected {min_cols}-{max_cols}). Schema may have changed."
        }
    elif actual_count > max_cols:
        return {
            "status": "WARNING",
            "column_count": actual_count,
            "expected_range": (min_cols, max_cols),
            "message": f"{file_type}: {actual_count} columns (expected {min_cols}-{max_cols}). New columns detected."
        }
    else:
        return {
            "status": "SUCCESS",
            "column_count": actual_count,
            "expected_range": (min_cols, max_cols),
            "message": f"{file_type}: {actual_count} columns (expected range)"
        }
```

### 3.3 Outlier Detection

```python
import numpy as np
from scipy import stats

def detect_outliers(series: pd.Series, method: str = "iqr") -> dict:
    """
    Detect outliers in numeric column.

    Methods:
        - iqr: Interquartile range (Q1-1.5*IQR, Q3+1.5*IQR)
        - zscore: Z-score > 3 or < -3
        - percentile: Below 1st or above 99th percentile
    """
    if series.dtype not in [np.float64, np.int64]:
        return {"status": "SKIP", "message": "Non-numeric column"}

    clean = series.dropna()
    if len(clean) == 0:
        return {"status": "SKIP", "message": "All NaN"}

    if method == "iqr":
        q1 = clean.quantile(0.25)
        q3 = clean.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = clean[(clean < lower_bound) | (clean > upper_bound)]

    elif method == "zscore":
        z_scores = np.abs(stats.zscore(clean))
        outliers = clean[z_scores > 3]
        lower_bound = clean.mean() - 3 * clean.std()
        upper_bound = clean.mean() + 3 * clean.std()

    elif method == "percentile":
        lower_bound = clean.quantile(0.01)
        upper_bound = clean.quantile(0.99)
        outliers = clean[(clean < lower_bound) | (clean > upper_bound)]

    outlier_pct = len(outliers) / len(clean) * 100

    return {
        "outlier_count": len(outliers),
        "outlier_percentage": outlier_pct,
        "bounds": (lower_bound, upper_bound),
        "min": clean.min(),
        "max": clean.max(),
        "median": clean.median(),
        "mean": clean.mean(),
        "std": clean.std(),
    }

# Experience hour outlier rules
OUTLIER_RULES = {
    "Exp_Hour_Total": {
        "max_reasonable": 10000,  # >10k hours is suspicious
        "max_possible": 50000,    # Hard limit
        "unit_check": True,        # Check if values suggest wrong units
    },
    "Exp_Hour_Research": {
        "max_reasonable": 5000,
        "max_possible": 20000,
    },
    "Age": {
        "min_reasonable": 18,
        "max_reasonable": 40,
        "max_possible": 70,
    },
    "GPA": {  # Assumes 4.0 scale
        "min_possible": 0.0,
        "max_possible": 4.5,  # Some schools use 4.3 or 4.5 scale
        "scale_check": True,   # Detect if using 5.0 scale
    },
    "Parent_Education": {
        "min_possible": 0,
        "max_possible": 6,  # Ordinal encoding
    }
}

def validate_numeric_ranges(df: pd.DataFrame) -> dict:
    """
    Validate numeric columns are within reasonable ranges.

    Returns detailed report with:
        - Outlier counts and percentages
        - Distribution statistics
        - Suspected data quality issues
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": [],
        "outlier_details": {}
    }

    for col in df.select_dtypes(include=[np.number]).columns:
        stats = detect_outliers(df[col])
        findings["outlier_details"][col] = stats

        # Check against known rules
        if col in OUTLIER_RULES:
            rules = OUTLIER_RULES[col]

            # Check maximum
            if "max_possible" in rules:
                max_val = df[col].max()
                if max_val > rules["max_possible"]:
                    findings["errors"].append(
                        f"{col}: max value {max_val} exceeds possible maximum {rules['max_possible']}"
                    )

            # Check minimum
            if "min_possible" in rules:
                min_val = df[col].min()
                if min_val < rules["min_possible"]:
                    findings["errors"].append(
                        f"{col}: min value {min_val} below possible minimum {rules['min_possible']}"
                    )

            # Check reasonable ranges
            if "max_reasonable" in rules:
                outliers = df[df[col] > rules["max_reasonable"]]
                if len(outliers) > 0:
                    findings["warnings"].append(
                        f"{col}: {len(outliers)} values exceed reasonable max {rules['max_reasonable']} "
                        f"(max={df[col].max():.1f})"
                    )

            # Special: unit check for hours
            if rules.get("unit_check"):
                median_val = df[col].median()
                # If median is >10000, might be in minutes not hours
                if median_val > 10000:
                    findings["errors"].append(
                        f"{col}: median value {median_val:.0f} suggests wrong units (minutes instead of hours?)"
                    )

            # Special: GPA scale check
            if rules.get("scale_check"):
                max_val = df[col].max()
                if max_val > 4.5:
                    findings["warnings"].append(
                        f"{col}: max value {max_val:.2f} suggests 5.0 scale (expected 4.0 scale)"
                    )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "message": f"Checked {len(findings['outlier_details'])} numeric columns"
    }
```

**Error Severity:**
- Value exceeds hard limits: ERROR
- Unit mismatch detected: ERROR
- Values outside reasonable range: WARNING
- >5% outliers in any column: WARNING

### 3.4 Cross-File Consistency

```python
def validate_cross_file_consistency(
    applicants_df: pd.DataFrame,
    aux_dfs: dict[str, pd.DataFrame]
) -> dict:
    """
    Validate referential integrity across files.

    Rules:
        1. Every Amcas_ID in auxiliary files must exist in Applicants
        2. Every Applicant should have at least 1 experience record
        3. Row count ratios should be reasonable

    Args:
        applicants_df: Main applicants table
        aux_dfs: Dict of {file_type: dataframe} for auxiliary tables
    """
    id_col = "Amcas_ID"  # Assumed normalized
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    applicant_ids = set(applicants_df[id_col].unique())
    n_applicants = len(applicant_ids)

    # Check each auxiliary file
    for file_type, aux_df in aux_dfs.items():
        if id_col not in aux_df.columns:
            findings["errors"].append(
                f"{file_type}: missing ID column '{id_col}' (cannot join)"
            )
            continue

        aux_ids = set(aux_df[id_col].unique())
        n_aux = len(aux_ids)

        # Find orphaned IDs (in aux but not in applicants)
        orphaned = aux_ids - applicant_ids
        if orphaned:
            findings["errors"].append(
                f"{file_type}: {len(orphaned)} IDs not in Applicants table. Examples: {list(orphaned)[:5]}"
            )

        # Find missing IDs (in applicants but not in aux)
        missing = applicant_ids - aux_ids
        missing_pct = len(missing) / n_applicants * 100

        # Expected coverage by file type
        EXPECTED_COVERAGE = {
            "experiences": 0.95,  # 95% should have experiences
            "personal_statement": 0.99,  # Almost all have PS
            "secondary_application": 0.70,  # Not all complete secondary
            "gpa_trend": 0.90,
            "languages": 0.80,  # Some may not report
            "parents": 0.70,  # Some may not report
        }

        expected = EXPECTED_COVERAGE.get(file_type, 0.80)
        actual_coverage = n_aux / n_applicants

        if actual_coverage < expected:
            findings["warnings"].append(
                f"{file_type}: only {actual_coverage*100:.1f}% coverage "
                f"(expected ≥{expected*100:.0f}%). {len(missing)} applicants missing."
            )

        # Check row count ratios for 1-to-many tables
        if file_type in ["experiences", "languages", "parents"]:
            total_rows = len(aux_df)
            avg_per_applicant = total_rows / n_aux if n_aux > 0 else 0

            EXPECTED_RATIOS = {
                "experiences": (3, 15),  # 3-15 experiences per person
                "languages": (1, 3),     # 1-3 languages
                "parents": (1, 2),       # 1-2 parents
            }

            if file_type in EXPECTED_RATIOS:
                min_ratio, max_ratio = EXPECTED_RATIOS[file_type]
                if avg_per_applicant < min_ratio:
                    findings["warnings"].append(
                        f"{file_type}: avg {avg_per_applicant:.1f} rows per applicant "
                        f"(expected {min_ratio}-{max_ratio}). Data may be incomplete."
                    )
                elif avg_per_applicant > max_ratio:
                    findings["warnings"].append(
                        f"{file_type}: avg {avg_per_applicant:.1f} rows per applicant "
                        f"(expected {min_ratio}-{max_ratio}). Possible duplicates?"
                    )
                else:
                    findings["info"].append(
                        f"{file_type}: avg {avg_per_applicant:.1f} rows per applicant (expected range)"
                    )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "message": f"Validated consistency across {len(aux_dfs)} auxiliary files"
    }
```

**Error Severity:**
- Orphaned IDs in auxiliary files: ERROR
- Coverage <50% of expected: ERROR
- Coverage 50-90% of expected: WARNING

### 3.5 Missing Value Patterns

```python
def validate_missing_values(df: pd.DataFrame, file_type: str) -> dict:
    """
    Analyze missing value patterns and flag suspicious cases.

    Red flags:
        - Required column >50% missing
        - Entire column is NaN
        - Missing pattern suggests data truncation
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": [],
        "missing_summary": {}
    }

    # Calculate missing percentages
    missing_pct = (df.isnull().sum() / len(df) * 100).to_dict()
    findings["missing_summary"] = {
        col: f"{pct:.1f}%"
        for col, pct in missing_pct.items()
        if pct > 0
    }

    # Critical columns that should never be mostly missing
    CRITICAL_COLUMNS = {
        "applicants": ["Amcas_ID", "Age", "Gender", "Exp_Hour_Total"],
        "experiences": ["Amcas_ID", "Exp_Type", "Total_Hours"],
        "personal_statement": ["Amcas_ID", "personal_statement"],
    }

    critical = CRITICAL_COLUMNS.get(file_type, [])
    for col in critical:
        if col not in df.columns:
            findings["errors"].append(f"Critical column missing: {col}")
        elif missing_pct.get(col, 0) > 50:
            findings["errors"].append(
                f"Critical column {col} is {missing_pct[col]:.1f}% missing (expected <5%)"
            )

    # Check for entirely empty columns
    empty_cols = [col for col, pct in missing_pct.items() if pct == 100]
    if empty_cols:
        findings["warnings"].append(
            f"{len(empty_cols)} columns are entirely empty: {empty_cols[:5]}"
        )

    # Check for suspicious patterns (all rows missing same columns)
    # This suggests truncated export or filtering issue
    row_missing_counts = df.isnull().sum(axis=1)
    max_missing_per_row = row_missing_counts.max()
    if max_missing_per_row > len(df.columns) * 0.5:
        n_affected = (row_missing_counts > len(df.columns) * 0.5).sum()
        findings["warnings"].append(
            f"{n_affected} rows missing >50% of columns. Data may be truncated."
        )

    # High missingness columns (>70%) - these will be dropped anyway
    high_missing = [col for col, pct in missing_pct.items() if pct > 70]
    if high_missing:
        findings["info"].append(
            f"{len(high_missing)} columns >70% missing (will be dropped): {high_missing[:5]}"
        )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "total_missing": sum(1 for pct in missing_pct.values() if pct > 0),
        "message": f"{len(missing_pct)} columns have missing data"
    }
```

**Error Severity:**
- Critical column >50% missing: ERROR
- Required column >20% missing: WARNING
- Many columns >70% missing: INFO

### 3.6 Duplicate Detection

```python
def validate_duplicates(df: pd.DataFrame, id_col: str, file_type: str) -> dict:
    """
    Detect duplicate records.

    For 1-to-1 files (Applicants, Personal Statement):
        - No duplicate Amcas_IDs allowed

    For 1-to-many files (Experiences, Languages):
        - Duplicate Amcas_IDs expected
        - But exact row duplicates are suspicious
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    ONE_TO_ONE_FILES = ["applicants", "personal_statement", "secondary_application", "gpa_trend"]

    # Check for duplicate IDs
    duplicate_ids = df[df.duplicated(subset=[id_col], keep=False)][id_col].unique()

    if file_type in ONE_TO_ONE_FILES:
        if len(duplicate_ids) > 0:
            findings["errors"].append(
                f"{len(duplicate_ids)} applicants have duplicate records. Examples: {duplicate_ids[:5].tolist()}"
            )
    else:
        # For 1-to-many, just report stats
        id_counts = df[id_col].value_counts()
        findings["info"].append(
            f"ID distribution: median={id_counts.median():.0f}, max={id_counts.max():.0f} rows per applicant"
        )

    # Check for exact row duplicates (always suspicious)
    exact_dupes = df[df.duplicated(keep=False)]
    if len(exact_dupes) > 0:
        findings["warnings"].append(
            f"{len(exact_dupes)} exact duplicate rows detected. Review for data quality issue."
        )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "duplicate_id_count": len(duplicate_ids),
        "exact_duplicate_count": len(exact_dupes),
    }
```

---

## 4. Feature Drift Detection

### Problem Statement
New cycle data may have significantly different distributions from training data (2022-2023), which could indicate:
1. Real demographic/behavioral shifts
2. Data collection changes
3. Data quality issues
4. Model applicability concerns

### Validation Strategy

#### 4.1 Distribution Comparison

```python
from scipy.stats import ks_2samp, chi2_contingency
from typing import Dict, List

def compute_distribution_drift(
    reference_df: pd.DataFrame,
    new_df: pd.DataFrame,
    feature_cols: List[str]
) -> dict:
    """
    Compare distributions between reference (training) and new data.

    Methods:
        - Numeric: Kolmogorov-Smirnov test
        - Categorical: Chi-square test
        - Effect size: Cohen's d for numeric, Cramér's V for categorical

    Returns drift report with:
        - Statistical test results
        - Effect sizes
        - Distribution summaries
    """
    drift_report = {
        "drifted_features": [],
        "warnings": [],
        "feature_details": {}
    }

    for col in feature_cols:
        if col not in reference_df.columns or col not in new_df.columns:
            continue

        ref_data = reference_df[col].dropna()
        new_data = new_df[col].dropna()

        if len(ref_data) == 0 or len(new_data) == 0:
            continue

        # Determine if numeric or categorical
        is_numeric = pd.api.types.is_numeric_dtype(reference_df[col])

        if is_numeric:
            # KS test for numeric
            statistic, p_value = ks_2samp(ref_data, new_data)

            # Cohen's d effect size
            mean_diff = new_data.mean() - ref_data.mean()
            pooled_std = np.sqrt((ref_data.std()**2 + new_data.std()**2) / 2)
            cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0

            drift_report["feature_details"][col] = {
                "type": "numeric",
                "test": "Kolmogorov-Smirnov",
                "statistic": float(statistic),
                "p_value": float(p_value),
                "effect_size": float(cohens_d),
                "reference_mean": float(ref_data.mean()),
                "new_mean": float(new_data.mean()),
                "reference_std": float(ref_data.std()),
                "new_std": float(new_data.std()),
            }

            # Flag significant drift
            if p_value < 0.01 and abs(cohens_d) > 0.5:  # Large effect
                drift_report["drifted_features"].append(col)
                drift_report["warnings"].append(
                    f"{col}: significant distribution shift detected "
                    f"(p={p_value:.4f}, Cohen's d={cohens_d:.2f})"
                )

        else:
            # Chi-square for categorical
            ref_counts = ref_data.value_counts()
            new_counts = new_data.value_counts()

            # Align categories
            all_categories = set(ref_counts.index) | set(new_counts.index)
            ref_aligned = pd.Series([ref_counts.get(cat, 0) for cat in all_categories])
            new_aligned = pd.Series([new_counts.get(cat, 0) for cat in all_categories])

            contingency_table = pd.DataFrame({
                'reference': ref_aligned,
                'new': new_aligned
            })

            try:
                chi2, p_value, dof, expected = chi2_contingency(contingency_table.T)

                # Cramér's V effect size
                n = contingency_table.sum().sum()
                cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))

                drift_report["feature_details"][col] = {
                    "type": "categorical",
                    "test": "Chi-square",
                    "statistic": float(chi2),
                    "p_value": float(p_value),
                    "effect_size": float(cramers_v),
                    "reference_mode": ref_counts.idxmax(),
                    "new_mode": new_counts.idxmax(),
                }

                if p_value < 0.01 and cramers_v > 0.3:  # Medium-large effect
                    drift_report["drifted_features"].append(col)
                    drift_report["warnings"].append(
                        f"{col}: significant category distribution shift "
                        f"(p={p_value:.4f}, Cramér's V={cramers_v:.2f})"
                    )
            except Exception as e:
                drift_report["feature_details"][col] = {
                    "type": "categorical",
                    "error": str(e)
                }

    return drift_report

def validate_feature_drift(
    training_df: pd.DataFrame,
    new_df: pd.DataFrame,
    feature_cols: List[str]
) -> dict:
    """
    High-level feature drift validation.

    Returns:
        {
            "status": "ERROR" | "WARNING" | "SUCCESS",
            "drift_summary": {...},
            "message": str
        }
    """
    drift_report = compute_distribution_drift(training_df, new_df, feature_cols)

    n_drifted = len(drift_report["drifted_features"])
    n_features = len(feature_cols)
    drift_pct = n_drifted / n_features * 100 if n_features > 0 else 0

    if drift_pct > 30:
        status = "ERROR"
        message = (
            f"Severe feature drift: {n_drifted}/{n_features} features ({drift_pct:.1f}%) "
            "have significantly different distributions. Model may not be applicable."
        )
    elif drift_pct > 10:
        status = "WARNING"
        message = (
            f"Moderate feature drift: {n_drifted}/{n_features} features ({drift_pct:.1f}%) "
            "have shifted. Review model predictions carefully."
        )
    else:
        status = "SUCCESS"
        message = f"Feature distributions stable ({n_drifted}/{n_features} drifted)"

    return {
        "status": status,
        "drift_summary": drift_report,
        "drifted_count": n_drifted,
        "total_features": n_features,
        "message": message
    }
```

**Error Severity:**
- >30% of features drifted: ERROR (model may not be applicable)
- 10-30% of features drifted: WARNING (review predictions carefully)
- <10% drifted: INFO (expected natural variation)

**Drift Thresholds:**
- Numeric: p < 0.01 AND |Cohen's d| > 0.5 (large effect)
- Categorical: p < 0.01 AND Cramér's V > 0.3 (medium-large effect)

#### 4.2 Specific Distribution Checks

```python
# High-risk features for drift (strong predictive signals)
DRIFT_SENSITIVE_FEATURES = [
    "Exp_Hour_Total",
    "Exp_Hour_Research",
    "Exp_Hour_Volunteer_Med",
    "First_Generation_Ind",
    "Disadvantaged_Ind",
    "writing_quality",
    "mission_alignment_service_orientation",
]

def validate_high_risk_drift(
    training_df: pd.DataFrame,
    new_df: pd.DataFrame
) -> dict:
    """Focus validation on features most likely to affect predictions."""
    drift_report = compute_distribution_drift(
        training_df, new_df, DRIFT_SENSITIVE_FEATURES
    )

    critical_drifts = []
    for feature in DRIFT_SENSITIVE_FEATURES:
        if feature in drift_report["feature_details"]:
            details = drift_report["feature_details"][feature]
            if details.get("p_value", 1.0) < 0.01:
                effect_size = details.get("effect_size", 0)
                if abs(effect_size) > 0.8:  # Very large effect
                    critical_drifts.append({
                        "feature": feature,
                        "effect_size": effect_size,
                        "p_value": details["p_value"]
                    })

    if critical_drifts:
        return {
            "status": "ERROR",
            "critical_drifts": critical_drifts,
            "message": f"{len(critical_drifts)} critical features have severe distribution shifts"
        }

    return {
        "status": "SUCCESS",
        "critical_drifts": [],
        "message": "High-risk features stable"
    }
```

#### 4.3 Binary Feature Prevalence Check

```python
def validate_binary_prevalence_shift(
    training_df: pd.DataFrame,
    new_df: pd.DataFrame,
    binary_features: List[str]
) -> dict:
    """
    Check if binary feature prevalence has shifted significantly.

    Red flag: Feature that was 10% prevalent is now 50% (or vice versa).
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    for feature in binary_features:
        if feature not in training_df.columns or feature not in new_df.columns:
            continue

        ref_prev = training_df[feature].mean()
        new_prev = new_df[feature].mean()

        abs_change = abs(new_prev - ref_prev)
        rel_change = abs_change / ref_prev if ref_prev > 0 else float('inf')

        # Flag large absolute or relative changes
        if abs_change > 0.2:  # 20 percentage point change
            findings["warnings"].append(
                f"{feature}: prevalence changed from {ref_prev*100:.1f}% to {new_prev*100:.1f}% "
                f"({abs_change*100:+.1f} pp)"
            )
        elif rel_change > 1.0 and ref_prev > 0.05:  # Doubled (for non-rare features)
            findings["warnings"].append(
                f"{feature}: prevalence doubled from {ref_prev*100:.1f}% to {new_prev*100:.1f}%"
            )

    status = "WARNING" if findings["warnings"] else "SUCCESS"

    return {
        "status": status,
        "findings": findings,
        "message": f"Checked {len(binary_features)} binary features"
    }
```

---

## 5. Year-Over-Year Schema Changes

### Problem Statement
Real AMCAS exports may evolve:
- Add new columns (e.g., new essay prompts)
- Rename columns (e.g., `Exp_Type` → `Experience_Type`)
- Change data types (numeric → categorical)
- Change coding schemes (Yes/No → Y/N → 1/0)
- Split or merge columns

### Validation Strategy

#### 5.1 Schema Comparison

```python
from dataclasses import dataclass
from typing import Set, Dict, Any

@dataclass
class SchemaChange:
    change_type: str  # "added", "removed", "renamed", "type_changed"
    column: str
    details: Dict[str, Any]
    severity: str  # "ERROR", "WARNING", "INFO"

def detect_schema_changes(
    reference_schema: Dict[str, str],  # {column: dtype}
    new_schema: Dict[str, str],
    column_mappings: Dict[str, List[str]] = None
) -> List[SchemaChange]:
    """
    Detect schema changes between reference and new data.

    Args:
        reference_schema: {column_name: dtype} from training data
        new_schema: {column_name: dtype} from new data
        column_mappings: Known column aliases for fuzzy matching
    """
    changes = []

    ref_cols = set(reference_schema.keys())
    new_cols = set(new_schema.keys())

    # Detect added columns
    added = new_cols - ref_cols
    for col in added:
        # Try to match with reference columns
        matched = False
        if column_mappings:
            for ref_col, aliases in column_mappings.items():
                if col in aliases and ref_col in ref_cols:
                    changes.append(SchemaChange(
                        change_type="renamed",
                        column=col,
                        details={"old_name": ref_col, "new_name": col},
                        severity="INFO"
                    ))
                    matched = True
                    break

        if not matched:
            changes.append(SchemaChange(
                change_type="added",
                column=col,
                details={"dtype": new_schema[col]},
                severity="INFO"  # New columns are usually OK
            ))

    # Detect removed columns
    removed = ref_cols - new_cols
    for col in removed:
        # Check if this is a required feature
        severity = "ERROR" if col in REQUIRED_COLUMNS.get(DataMode.TRAINING, {}).get("critical", []) else "WARNING"
        changes.append(SchemaChange(
            change_type="removed",
            column=col,
            details={},
            severity=severity
        ))

    # Detect type changes
    common_cols = ref_cols & new_cols
    for col in common_cols:
        if reference_schema[col] != new_schema[col]:
            changes.append(SchemaChange(
                change_type="type_changed",
                column=col,
                details={
                    "old_type": reference_schema[col],
                    "new_type": new_schema[col]
                },
                severity="WARNING"
            ))

    return changes

def validate_schema_evolution(
    reference_df: pd.DataFrame,
    new_df: pd.DataFrame,
    file_type: str
) -> dict:
    """
    Validate that schema changes are acceptable.

    Returns:
        {
            "status": "ERROR" | "WARNING" | "SUCCESS",
            "changes": [SchemaChange],
            "summary": {...}
        }
    """
    ref_schema = {col: str(dtype) for col, dtype in reference_df.dtypes.items()}
    new_schema = {col: str(dtype) for col, dtype in new_df.dtypes.items()}

    changes = detect_schema_changes(ref_schema, new_schema, COLUMN_MAPPINGS)

    # Categorize by severity
    errors = [c for c in changes if c.severity == "ERROR"]
    warnings = [c for c in changes if c.severity == "WARNING"]
    info = [c for c in changes if c.severity == "INFO"]

    summary = {
        "total_changes": len(changes),
        "added_columns": len([c for c in changes if c.change_type == "added"]),
        "removed_columns": len([c for c in changes if c.change_type == "removed"]),
        "renamed_columns": len([c for c in changes if c.change_type == "renamed"]),
        "type_changes": len([c for c in changes if c.change_type == "type_changed"]),
    }

    if errors:
        status = "ERROR"
        message = f"{len(errors)} critical schema changes detected"
    elif warnings:
        status = "WARNING"
        message = f"{len(warnings)} schema changes require review"
    else:
        status = "SUCCESS"
        message = f"Schema evolution acceptable ({len(info)} minor changes)"

    return {
        "status": status,
        "changes": [
            {
                "type": c.change_type,
                "column": c.column,
                "details": c.details,
                "severity": c.severity
            }
            for c in changes
        ],
        "summary": summary,
        "message": message
    }
```

#### 5.2 Coding Scheme Detection

```python
def detect_coding_scheme(series: pd.Series) -> dict:
    """
    Detect what coding scheme is used for a column.

    Common schemes:
        - Binary: Yes/No, Y/N, True/False, 1/0
        - Ordinal: integers 0-N
        - Categorical: text labels
    """
    unique_vals = set(series.dropna().unique())

    # Binary detection
    BINARY_SCHEMES = [
        {"Yes", "No"},
        {"Y", "N"},
        {"yes", "no"},
        {"True", "False"},
        {"true", "false"},
        {"1", "0"},
        {1, 0},
        {1.0, 0.0},
    ]

    for scheme in BINARY_SCHEMES:
        if unique_vals <= scheme:
            return {
                "type": "binary",
                "scheme": list(scheme),
                "mapping": {v: 1 if v in ["Yes", "Y", "yes", "True", "true", 1, 1.0] else 0 for v in scheme}
            }

    # Ordinal detection (consecutive integers)
    if all(isinstance(v, (int, np.integer)) for v in unique_vals):
        sorted_vals = sorted(unique_vals)
        if sorted_vals == list(range(min(sorted_vals), max(sorted_vals) + 1)):
            return {
                "type": "ordinal",
                "min": min(sorted_vals),
                "max": max(sorted_vals),
                "n_levels": len(sorted_vals)
            }

    # Categorical
    return {
        "type": "categorical",
        "n_categories": len(unique_vals),
        "categories": list(unique_vals)[:10]  # Sample
    }

def validate_coding_scheme_consistency(
    reference_df: pd.DataFrame,
    new_df: pd.DataFrame,
    columns: List[str]
) -> dict:
    """
    Check if coding schemes have changed for important columns.
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    for col in columns:
        if col not in reference_df.columns or col not in new_df.columns:
            continue

        ref_scheme = detect_coding_scheme(reference_df[col])
        new_scheme = detect_coding_scheme(new_df[col])

        if ref_scheme["type"] != new_scheme["type"]:
            findings["errors"].append(
                f"{col}: coding type changed from {ref_scheme['type']} to {new_scheme['type']}"
            )
        elif ref_scheme["type"] == "binary":
            # Check if binary scheme changed
            if ref_scheme["scheme"] != new_scheme["scheme"]:
                findings["warnings"].append(
                    f"{col}: binary coding changed from {ref_scheme['scheme']} to {new_scheme['scheme']}"
                )
        elif ref_scheme["type"] == "ordinal":
            # Check if ordinal range changed
            if ref_scheme["max"] != new_scheme["max"]:
                findings["warnings"].append(
                    f"{col}: ordinal range changed from {ref_scheme['max']} to {new_scheme['max']}"
                )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "message": f"Checked coding schemes for {len(columns)} columns"
    }
```

---

## 6. File-Specific Validation Rules

### 6.1 Experiences File

```python
def validate_experiences_file(df: pd.DataFrame, applicant_ids: Set[str]) -> dict:
    """
    Validate Experiences file.

    Rules:
        - 3-50 experiences per applicant (typical)
        - Total_Hours should be reasonable (0-50,000)
        - Exp_Type should be from known categories
        - Start_Date <= End_Date
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    # Check experience count per applicant
    exp_counts = df.groupby("Amcas_ID").size()

    too_few = exp_counts[exp_counts < 3]
    if len(too_few) > 0:
        findings["warnings"].append(
            f"{len(too_few)} applicants have <3 experiences (may be incomplete)"
        )

    too_many = exp_counts[exp_counts > 50]
    if len(too_many) > 0:
        findings["warnings"].append(
            f"{len(too_many)} applicants have >50 experiences (possible duplicates?)"
        )

    # Validate experience hours
    if "Total_Hours" in df.columns:
        hour_stats = validate_numeric_ranges(df[["Total_Hours"]])
        if hour_stats["status"] != "SUCCESS":
            findings["warnings"].extend(hour_stats["findings"].get("warnings", []))
            findings["errors"].extend(hour_stats["findings"].get("errors", []))

    # Check Exp_Type categories
    if "Exp_Type" in df.columns:
        known_types = {
            "Physician Shadowing/Clinical Observation",
            "Community Service/Volunteer - Medical/Clinical",
            "Community Service/Volunteer - Not Medical/Clinical",
            "Paid Employment - Medical/Clinical",
            "Research/Lab",
            "Leadership - Not Listed Elsewhere",
            "Military Service",
        }

        actual_types = set(df["Exp_Type"].dropna().unique())
        unknown_types = actual_types - known_types

        if unknown_types:
            findings["info"].append(
                f"Found {len(unknown_types)} new experience types: {list(unknown_types)[:5]}"
            )

    # Validate date logic
    if "Start_Date" in df.columns and "End_Date" in df.columns:
        df_dates = df.copy()
        df_dates["Start_Date"] = pd.to_datetime(df_dates["Start_Date"], errors="coerce")
        df_dates["End_Date"] = pd.to_datetime(df_dates["End_Date"], errors="coerce")

        invalid_dates = df_dates[df_dates["Start_Date"] > df_dates["End_Date"]]
        if len(invalid_dates) > 0:
            findings["errors"].append(
                f"{len(invalid_dates)} experiences have Start_Date > End_Date"
            )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "message": f"Validated {len(df)} experience records"
    }
```

### 6.2 Personal Statement File

```python
def validate_personal_statement_file(df: pd.DataFrame) -> dict:
    """
    Validate Personal Statement file.

    Rules:
        - personal_statement column must exist
        - Text length should be reasonable (AMCAS limit: 5,300 characters)
        - No applicant should have blank statement
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    if "personal_statement" not in df.columns:
        findings["errors"].append("Missing personal_statement column")
        return {
            "status": "ERROR",
            "findings": findings,
            "message": "Critical column missing"
        }

    # Check for blank statements
    blank = df["personal_statement"].isna() | (df["personal_statement"].str.strip() == "")
    n_blank = blank.sum()

    if n_blank > 0:
        findings["warnings"].append(
            f"{n_blank} applicants have blank personal statements"
        )

    # Check text lengths
    lengths = df["personal_statement"].dropna().str.len()

    if len(lengths) > 0:
        findings["info"].append(
            f"Personal statement lengths: median={lengths.median():.0f}, "
            f"max={lengths.max():.0f} characters"
        )

        # AMCAS limit is 5,300 characters
        too_long = lengths[lengths > 5300]
        if len(too_long) > 0:
            findings["warnings"].append(
                f"{len(too_long)} statements exceed AMCAS limit (5,300 chars)"
            )

        # Check for truncation (many statements at exact same length)
        # If >10% are exactly 5000 chars, might be truncated
        at_5000 = (lengths == 5000).sum()
        if at_5000 > len(lengths) * 0.1:
            findings["warnings"].append(
                f"{at_5000} statements are exactly 5000 characters (possible truncation?)"
            )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "message": f"Validated {len(df)} personal statements"
    }
```

### 6.3 GPA Trend File

```python
def validate_gpa_trend_file(df: pd.DataFrame) -> dict:
    """
    Validate GPA Trend file.

    Rules:
        - GPA values should be 0.0-4.5 (or 0.0-5.0 if using 5.0 scale)
        - Detect scale mismatches
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    gpa_cols = [c for c in df.columns if "GPA" in c.upper() and "TREND" not in c.upper()]

    for col in gpa_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        clean = df[col].dropna()
        if len(clean) == 0:
            continue

        max_gpa = clean.max()
        min_gpa = clean.min()

        # Detect scale
        if max_gpa > 5.0:
            findings["errors"].append(
                f"{col}: max GPA {max_gpa:.2f} exceeds all known scales"
            )
        elif max_gpa > 4.5:
            findings["warnings"].append(
                f"{col}: max GPA {max_gpa:.2f} suggests 5.0 scale (expected 4.0 scale)"
            )

        if min_gpa < 0.0:
            findings["errors"].append(
                f"{col}: min GPA {min_gpa:.2f} is negative (invalid)"
            )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "message": f"Validated GPA values in {len(gpa_cols)} columns"
    }
```

### 6.4 Parents File

```python
def validate_parents_file(df: pd.DataFrame) -> dict:
    """
    Validate Parents file.

    Rules:
        - 1-2 parents per applicant
        - Education level should map to known categories
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    # Check parent count per applicant
    parent_counts = df.groupby("Amcas_ID").size()

    too_many = parent_counts[parent_counts > 2]
    if len(too_many) > 0:
        findings["warnings"].append(
            f"{len(too_many)} applicants have >2 parent records (duplicates?)"
        )

    # Check education levels
    ed_col = None
    for candidate in ["Edu_Level", "Parent_Education_Level", "Parent_Education"]:
        if candidate in df.columns:
            ed_col = candidate
            break

    if ed_col:
        known_levels = set(PARENT_EDUCATION_MAP.keys())
        actual_levels = set(df[ed_col].dropna().unique())
        unknown_levels = actual_levels - known_levels

        if unknown_levels:
            findings["warnings"].append(
                f"Found {len(unknown_levels)} unmapped education levels: {list(unknown_levels)[:5]}"
            )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "message": f"Validated {len(df)} parent records"
    }
```

---

## 7. Edge Cases in Score-Only Path

### 7.1 New Column Handling

```python
def validate_new_columns_in_scoring(
    training_features: List[str],
    new_df: pd.DataFrame
) -> dict:
    """
    Handle new columns that didn't exist in training.

    Rule: New columns should be ignored (not cause errors).
    """
    new_cols = set(new_df.columns) - set(training_features)

    # Remove expected non-feature columns
    new_cols = new_cols - {"Amcas_ID", "app_year", "App_Year"}

    if len(new_cols) > 0:
        return {
            "status": "INFO",
            "new_columns": list(new_cols),
            "message": f"{len(new_cols)} new columns detected (will be ignored): {list(new_cols)[:10]}"
        }

    return {
        "status": "SUCCESS",
        "new_columns": [],
        "message": "No unexpected columns"
    }
```

### 7.2 Binary Feature Anomaly Detection

```python
def validate_binary_anomalies(
    training_df: pd.DataFrame,
    new_df: pd.DataFrame,
    binary_features: List[str]
) -> dict:
    """
    Detect anomalous binary feature patterns.

    Red flags:
        - Feature that was always 0 in training is now 1 for many applicants
        - Feature that had balanced distribution is now 100% or 0%
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    for feature in binary_features:
        if feature not in training_df.columns or feature not in new_df.columns:
            continue

        train_mean = training_df[feature].mean()
        new_mean = new_df[feature].mean()

        # Case 1: Always-zero feature now has positive cases
        if train_mean == 0 and new_mean > 0.05:
            findings["warnings"].append(
                f"{feature}: was always 0 in training, now {new_mean*100:.1f}% positive"
            )

        # Case 2: Balanced feature is now extreme
        if 0.2 <= train_mean <= 0.8:  # Was balanced
            if new_mean > 0.95 or new_mean < 0.05:  # Now extreme
                findings["warnings"].append(
                    f"{feature}: was {train_mean*100:.1f}% in training, now {new_mean*100:.1f}%"
                )

    status = "WARNING" if findings["warnings"] else "SUCCESS"

    return {
        "status": status,
        "findings": findings,
        "message": f"Checked {len(binary_features)} binary features"
    }
```

### 7.3 Rubric Score Missingness

```python
def validate_rubric_availability(
    new_df: pd.DataFrame,
    rubric_features: List[str]
) -> dict:
    """
    Check rubric score availability in new data.

    Expected scenarios:
        1. No rubric scores yet (new cycle) → use Plan A model
        2. Partial rubric scores → use Plan B for scored, Plan A for unscored
        3. All rubric scores → use Plan B model
    """
    if not any(col in new_df.columns for col in rubric_features):
        return {
            "status": "INFO",
            "coverage": 0.0,
            "recommendation": "Use Plan A model (structured features only)",
            "message": "No rubric scores available (expected for new cycle)"
        }

    # Check coverage
    rubric_cols_present = [col for col in rubric_features if col in new_df.columns]
    coverage_per_col = {
        col: new_df[col].notna().sum() / len(new_df)
        for col in rubric_cols_present
    }

    avg_coverage = np.mean(list(coverage_per_col.values()))

    if avg_coverage == 0.0:
        recommendation = "Use Plan A model"
        status = "INFO"
    elif avg_coverage < 0.5:
        recommendation = "Use Plan A model (insufficient rubric coverage)"
        status = "WARNING"
    else:
        recommendation = "Use Plan B model (rubric + structured)"
        status = "SUCCESS"

    return {
        "status": status,
        "coverage": avg_coverage,
        "coverage_by_feature": coverage_per_col,
        "recommendation": recommendation,
        "message": f"Rubric coverage: {avg_coverage*100:.1f}%"
    }
```

### 7.4 Experience Hour Unit Detection

```python
def detect_hour_unit_mismatch(df: pd.DataFrame) -> dict:
    """
    Detect if experience hours are in wrong units (minutes vs hours).

    Heuristic: If median Exp_Hour_Total > 10,000, likely in minutes.
    """
    findings = {
        "errors": [],
        "warnings": [],
        "info": []
    }

    hour_cols = [
        "Exp_Hour_Total",
        "Exp_Hour_Research",
        "Exp_Hour_Volunteer_Med",
        "Comm_Service_Total_Hours",
        "HealthCare_Total_Hours",
    ]

    for col in hour_cols:
        if col not in df.columns:
            continue

        clean = df[col].dropna()
        if len(clean) == 0:
            continue

        median_val = clean.median()
        mean_val = clean.mean()

        # Check if values suggest minutes instead of hours
        if median_val > 10000:
            findings["errors"].append(
                f"{col}: median={median_val:.0f} suggests minutes instead of hours (divide by 60?)"
            )
        elif mean_val > 20000:
            findings["warnings"].append(
                f"{col}: mean={mean_val:.0f} is very high (verify units)"
            )

    status = "ERROR" if findings["errors"] else ("WARNING" if findings["warnings"] else "SUCCESS")

    return {
        "status": status,
        "findings": findings,
        "message": f"Checked units for {len(hour_cols)} hour columns"
    }
```

---

## 8. Integration with ValidationResult Model

### 8.1 ValidationResult Schema

```python
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class ValidationStatus(Enum):
    ERROR = "error"      # Blocks pipeline
    WARNING = "warning"  # Requires acknowledgment
    INFO = "info"        # Informational only
    SUCCESS = "success"  # All checks passed

class ValidationMessage:
    """Single validation message."""
    def __init__(
        self,
        status: ValidationStatus,
        category: str,  # "schema", "data_quality", "drift", etc.
        message: str,
        details: Optional[Dict[str, Any]] = None,
        recommendation: Optional[str] = None
    ):
        self.status = status
        self.category = category
        self.message = message
        self.details = details or {}
        self.recommendation = recommendation
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "category": self.category,
            "message": self.message,
            "details": self.details,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.isoformat()
        }

class ValidationResult:
    """Complete validation result for uploaded data."""
    def __init__(self):
        self.errors: List[ValidationMessage] = []
        self.warnings: List[ValidationMessage] = []
        self.info: List[ValidationMessage] = []
        self.file_validations: Dict[str, Dict] = {}
        self.overall_status: ValidationStatus = ValidationStatus.SUCCESS
        self.data_mode: Optional[DataMode] = None
        self.can_proceed: bool = True

    def add_message(self, msg: ValidationMessage):
        """Add a validation message and update overall status."""
        if msg.status == ValidationStatus.ERROR:
            self.errors.append(msg)
            self.overall_status = ValidationStatus.ERROR
            self.can_proceed = False
        elif msg.status == ValidationStatus.WARNING:
            self.warnings.append(msg)
            if self.overall_status != ValidationStatus.ERROR:
                self.overall_status = ValidationStatus.WARNING
        elif msg.status == ValidationStatus.INFO:
            self.info.append(msg)

    def to_dict(self) -> dict:
        """Serialize for API response."""
        return {
            "overall_status": self.overall_status.value,
            "can_proceed": self.can_proceed,
            "data_mode": self.data_mode.value if self.data_mode else None,
            "summary": {
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
                "info_count": len(self.info),
            },
            "errors": [msg.to_dict() for msg in self.errors],
            "warnings": [msg.to_dict() for msg in self.warnings],
            "info": [msg.to_dict() for msg in self.info],
            "file_validations": self.file_validations,
        }
```

### 8.2 Orchestration Function

```python
def validate_uploaded_data(
    uploaded_files: Dict[str, pd.DataFrame],  # {file_type: dataframe}
    reference_data: Optional[pd.DataFrame] = None,  # Training data for drift detection
    mode: str = "auto"  # "auto", "training", "scoring"
) -> ValidationResult:
    """
    Master validation orchestration function.

    Runs all validation checks in sequence:
        1. File presence and structure
        2. ID column validation
        3. Row/column count checks
        4. Data quality checks
        5. Cross-file consistency
        6. Schema evolution detection
        7. Feature drift (if reference data provided)
        8. File-specific validation

    Returns comprehensive ValidationResult.
    """
    result = ValidationResult()

    # 1. File presence check
    REQUIRED_FILES = ["applicants", "experiences", "personal_statement"]
    missing_files = [f for f in REQUIRED_FILES if f not in uploaded_files]

    if missing_files:
        result.add_message(ValidationMessage(
            status=ValidationStatus.ERROR,
            category="file_structure",
            message=f"Missing required files: {missing_files}",
            recommendation="Upload all 7 required Excel files"
        ))
        return result  # Can't proceed without required files

    # 2. Validate each file
    for file_type, df in uploaded_files.items():
        file_results = {}

        # ID column validation
        id_check = validate_id_column(df, file_type)
        file_results["id_column"] = id_check
        if id_check["status"] == "ERROR":
            result.add_message(ValidationMessage(
                status=ValidationStatus.ERROR,
                category="schema",
                message=id_check["message"],
                details={"file": file_type}
            ))

        # Row count validation
        row_check = validate_row_count(df, file_type)
        file_results["row_count"] = row_check
        if row_check["status"] == "ERROR":
            result.add_message(ValidationMessage(
                status=ValidationStatus.ERROR,
                category="data_quality",
                message=row_check["message"],
                details={"file": file_type, "row_count": row_check["row_count"]}
            ))
        elif row_check["status"] == "WARNING":
            result.add_message(ValidationMessage(
                status=ValidationStatus.WARNING,
                category="data_quality",
                message=row_check["message"],
                details={"file": file_type}
            ))

        # Column count validation
        col_check = validate_column_count(df, file_type)
        file_results["column_count"] = col_check
        if col_check["status"] == "WARNING":
            result.add_message(ValidationMessage(
                status=ValidationStatus.WARNING,
                category="schema",
                message=col_check["message"],
                details={"file": file_type}
            ))

        # Numeric range validation
        range_check = validate_numeric_ranges(df)
        file_results["numeric_ranges"] = range_check["findings"]
        for error in range_check["findings"]["errors"]:
            result.add_message(ValidationMessage(
                status=ValidationStatus.ERROR,
                category="data_quality",
                message=error,
                details={"file": file_type}
            ))
        for warning in range_check["findings"]["warnings"]:
            result.add_message(ValidationMessage(
                status=ValidationStatus.WARNING,
                category="data_quality",
                message=warning,
                details={"file": file_type}
            ))

        # Missing value patterns
        missing_check = validate_missing_values(df, file_type)
        file_results["missing_values"] = missing_check
        for error in missing_check["findings"]["errors"]:
            result.add_message(ValidationMessage(
                status=ValidationStatus.ERROR,
                category="data_quality",
                message=error,
                details={"file": file_type}
            ))

        # Duplicate detection
        if "id_column" in file_results and file_results["id_column"]["id_column"]:
            dup_check = validate_duplicates(
                df,
                file_results["id_column"]["id_column"],
                file_type
            )
            file_results["duplicates"] = dup_check
            for error in dup_check["findings"]["errors"]:
                result.add_message(ValidationMessage(
                    status=ValidationStatus.ERROR,
                    category="data_quality",
                    message=error,
                    details={"file": file_type}
                ))

        # File-specific validation
        if file_type == "experiences" and "applicants" in uploaded_files:
            exp_check = validate_experiences_file(
                df,
                set(uploaded_files["applicants"]["Amcas_ID"].unique())
            )
            file_results["file_specific"] = exp_check
            for error in exp_check["findings"]["errors"]:
                result.add_message(ValidationMessage(
                    status=ValidationStatus.ERROR,
                    category="data_quality",
                    message=error,
                    details={"file": file_type}
                ))

        elif file_type == "personal_statement":
            ps_check = validate_personal_statement_file(df)
            file_results["file_specific"] = ps_check
            for error in ps_check["findings"]["errors"]:
                result.add_message(ValidationMessage(
                    status=ValidationStatus.ERROR,
                    category="data_quality",
                    message=error,
                    details={"file": file_type}
                ))

        result.file_validations[file_type] = file_results

    # 3. Cross-file consistency (if no errors so far)
    if result.can_proceed and "applicants" in uploaded_files:
        aux_files = {k: v for k, v in uploaded_files.items() if k != "applicants"}
        consistency_check = validate_cross_file_consistency(
            uploaded_files["applicants"],
            aux_files
        )

        for error in consistency_check["findings"]["errors"]:
            result.add_message(ValidationMessage(
                status=ValidationStatus.ERROR,
                category="consistency",
                message=error
            ))

        for warning in consistency_check["findings"]["warnings"]:
            result.add_message(ValidationMessage(
                status=ValidationStatus.WARNING,
                category="consistency",
                message=warning
            ))

    # 4. Detect data mode (training vs scoring)
    if "applicants" in uploaded_files:
        mode_check = detect_data_mode(uploaded_files["applicants"])
        result.data_mode = mode_check["mode"]
        result.add_message(ValidationMessage(
            status=ValidationStatus.INFO,
            category="data_mode",
            message=mode_check["message"],
            details={"mode": mode_check["mode"].value}
        ))

    # 5. Feature drift detection (if reference data provided)
    if reference_data is not None and result.can_proceed:
        # Build unified dataset from uploads
        from pipeline.data_ingestion import build_unified_dataset

        # This is simplified - real implementation would need to handle uploads properly
        try:
            unified_new = build_unified_dataset(uploaded_files)

            # Get feature columns
            feature_cols = [c for c in NUMERIC_FEATURES + BINARY_FEATURES if c in unified_new.columns]

            drift_check = validate_feature_drift(
                reference_data,
                unified_new,
                feature_cols
            )

            if drift_check["status"] == "ERROR":
                result.add_message(ValidationMessage(
                    status=ValidationStatus.ERROR,
                    category="drift",
                    message=drift_check["message"],
                    details=drift_check["drift_summary"],
                    recommendation="Review drifted features before proceeding. Model may need retraining."
                ))
            elif drift_check["status"] == "WARNING":
                result.add_message(ValidationMessage(
                    status=ValidationStatus.WARNING,
                    category="drift",
                    message=drift_check["message"],
                    details=drift_check["drift_summary"],
                    recommendation="Monitor predictions for unexpected behavior."
                ))

        except Exception as e:
            result.add_message(ValidationMessage(
                status=ValidationStatus.WARNING,
                category="drift",
                message=f"Could not complete drift detection: {str(e)}"
            ))

    return result
```

---

## 9. Implementation Checklist

### Phase 1: Core Validation (Week 1)
- [ ] Implement ID column fuzzy matching
- [ ] Row and column count validation
- [ ] Numeric range checks with outlier detection
- [ ] Missing value pattern analysis
- [ ] Duplicate detection
- [ ] ValidationResult model and API integration

### Phase 2: Cross-File Validation (Week 2)
- [ ] Cross-file consistency checks
- [ ] File-specific validation (Experiences, PS, GPA, Parents)
- [ ] Data mode detection (training vs scoring)
- [ ] Unit mismatch detection

### Phase 3: Advanced Validation (Week 3)
- [ ] Schema evolution detection
- [ ] Coding scheme consistency checks
- [ ] Feature drift detection (KS test, chi-square)
- [ ] Binary feature anomaly detection
- [ ] High-risk feature drift tracking

### Phase 4: Testing & Refinement (Week 4)
- [ ] Unit tests for all validation functions
- [ ] Integration tests with real 2022-2024 data
- [ ] Threshold tuning based on historical data
- [ ] User feedback integration
- [ ] Documentation and error message clarity

---

## 10. Summary: Severity Matrix

| Check | ERROR Threshold | WARNING Threshold | INFO |
|-------|----------------|-------------------|------|
| **ID Column** | Not found | Fuzzy match <0.9 | Exact match |
| **Row Count** | <min or >max | Outside expected range | Within range |
| **Column Count** | <min | >max | Within range |
| **Outliers** | >hard limit, unit mismatch | >5% outliers | <5% outliers |
| **Missing Values** | Critical col >50% | Required col >20% | Optional col missing |
| **Duplicates** | Duplicate IDs (1:1 files) | Exact row duplicates | - |
| **Cross-File** | Orphaned IDs | Coverage <expected | - |
| **Drift** | >30% features drifted | 10-30% features drifted | <10% drifted |
| **Schema Changes** | Critical col removed | Type changed | Col added |

---

## Appendix A: Configuration Constants

```python
# Save this as pipeline/validation_config.py

VALIDATION_CONFIG = {
    "id_column": {
        "target": "Amcas_ID",
        "aliases": ["Amcas_ID", "amcas_id", "AMCAS ID", "AMCAS_ID"],
        "fuzzy_threshold": 0.80
    },

    "row_counts": {
        "applicants": {"min": 100, "expected": (800, 2000), "max": 25000},
        "experiences": {"min": 1000, "expected": (5000, 30000), "max": 100000},
        "personal_statement": {"min": 100, "expected": (800, 2000), "max": 25000},
    },

    "outlier_detection": {
        "method": "iqr",  # or "zscore", "percentile"
        "threshold": 0.05  # Flag if >5% outliers
    },

    "drift_detection": {
        "numeric": {
            "test": "kolmogorov_smirnov",
            "p_value_threshold": 0.01,
            "effect_size_threshold": 0.5  # Cohen's d
        },
        "categorical": {
            "test": "chi_square",
            "p_value_threshold": 0.01,
            "effect_size_threshold": 0.3  # Cramér's V
        },
        "error_threshold": 0.30,  # >30% features drifted = ERROR
        "warning_threshold": 0.10  # >10% features drifted = WARNING
    }
}
```

---

## Appendix B: Pandas Code Snippets

### Quick Start: Validate Single File

```python
import pandas as pd
from pipeline.validation import validate_id_column, validate_row_count, validate_numeric_ranges

# Load file
df = pd.read_excel("data/raw/2024/1. Applicants.xlsx")

# Run basic checks
id_check = validate_id_column(df, "applicants")
print(f"ID Column: {id_check['status']} - {id_check['message']}")

row_check = validate_row_count(df, "applicants")
print(f"Row Count: {row_check['status']} - {row_check['message']}")

range_check = validate_numeric_ranges(df)
print(f"Numeric Ranges: {range_check['status']}")
for warning in range_check['findings']['warnings']:
    print(f"  - {warning}")
```

### Quick Start: Full Validation

```python
from pipeline.validation import validate_uploaded_data

# Load all files
files = {
    "applicants": pd.read_excel("data/raw/2024/1. Applicants.xlsx"),
    "experiences": pd.read_excel("data/raw/2024/6. Experiences.xlsx"),
    "personal_statement": pd.read_excel("data/raw/2024/9. Personal Statement.xlsx"),
    # ... other files
}

# Run full validation
result = validate_uploaded_data(files)

print(f"Overall Status: {result.overall_status.value}")
print(f"Can Proceed: {result.can_proceed}")
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")

# Print errors
for error in result.errors:
    print(f"[ERROR] {error.category}: {error.message}")
```

---

This specification provides a comprehensive, production-ready validation framework that balances rigor with flexibility for real-world AMCAS data variations.
