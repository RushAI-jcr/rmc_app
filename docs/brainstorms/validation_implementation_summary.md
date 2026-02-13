# Data Validation Implementation Summary

## Executive Summary

This document summarizes the comprehensive data validation specification for the Rush Medical College admissions triage system. The validation system must handle ~17,000 AMCAS applicants annually from 7 Excel files while managing column name variations, schema evolution, and data quality issues.

---

## Critical Findings from Pipeline Analysis

### Current Pipeline Assumptions

1. **Column Name Normalization**: Spaces → underscores, remove parentheses
2. **ID Column Handling**: Multiple aliases handled (`Amcas_ID`, `amcas_id`, `AMCAS ID`)
3. **Known Data Issues**:
   - Typo in 2024 data: `Disadvantanged_Ind` (should be `Disadvantaged_Ind`)
   - Schools file name varies by year: `8. Schools.xlsx` (2022-2023) vs `8. School.xlsx` (2024)
   - Experience hours stored as numeric (0-50,000 reasonable range)
   - Binary indicators use multiple schemes: Yes/No, Y/N, 1/0

### Data Flow Architecture

```
1. Load 7 xlsx files → normalize column names → normalize ID column
2. Aggregate 1-to-many tables (Languages, Parents, GPA Trend, Experiences)
3. Join all tables on Amcas_ID
4. Create binary features from Yes/No columns
5. Engineer composite features (Total_Volunteer_Hours, Adversity_Count, etc.)
6. Extract 46 features (21 structured + 7 engineered + 9 binary flags + 9 rubric)
7. Feed to two-stage model (Gate → Ranker)
```

---

## Key Validation Questions: Answers

### 1. Column Name Evolution Strategy

**Implementation:** Three-tier fuzzy matching

```python
# Tier 1: Exact match (after normalization)
normalized = col.lower().replace(" ", "_").replace("(", "").replace(")", "")

# Tier 2: Known aliases (from config)
COLUMN_MAPPINGS = {
    "Exp_Type": ["Exp_Type", "Experience_Type", "exp_type"],
    "Disadvantaged_Ind": ["Disadvantaged_Ind", "Disadvantanged_Ind"],  # Known typo
}

# Tier 3: Fuzzy match with SequenceMatcher (threshold: 0.85)
ratio = SequenceMatcher(None, normalized_col, target_col).ratio()
```

**Decision Rules:**
- Confidence ≥ 1.0 (exact): SUCCESS, proceed
- Confidence ≥ 0.85 (fuzzy): WARNING, log match and proceed
- Confidence < 0.85: Check if required feature
  - Required: ERROR, block pipeline
  - Optional: WARNING, proceed without feature

**Critical vs Optional Features:**
- **Critical** (block pipeline if missing): `Amcas_ID`, `Age`, `Gender`, `Exp_Hour_Total`
- **Important** (warn but proceed): Most other features
- **Optional** (info only): High-missingness columns already in `COLUMNS_TO_DROP`

### 2. Missing Target Column Handling

**Data Mode Detection:**

```python
class DataMode(Enum):
    TRAINING = "training"  # Historical data with Application_Review_Score
    SCORING = "scoring"    # New applicants (no scores yet)
    MIXED = "mixed"        # Partial scores (ERROR condition)
```

**Rules:**
- **TRAINING mode** (coverage ≥ 95%): Requires target column, validates against historical distributions
- **SCORING mode** (coverage = 0%): No target required, use model to predict scores
- **MIXED mode** (0% < coverage < 95%): ERROR - inconsistent data, cannot determine intent

**Columns Absent in New Data:**

| Column | Expected in Scoring? | Severity if Missing |
|--------|---------------------|---------------------|
| `Application_Review_Score` | No (target) | INFO |
| `Service_Rating_Categorical` | No (target) | INFO |
| `Prev_Applied_Rush` | Maybe | WARNING |
| All AMCAS fields | Yes | ERROR |
| Experience fields | Yes | ERROR |
| Financial fields | Yes | ERROR |

### 3. Data Quality Red Flags

#### Row Count Validation

| File | Min | Expected Range | Max | Description |
|------|-----|----------------|-----|-------------|
| Applicants | 100 | 800-2,000 | 25,000 | One per applicant |
| Experiences | 1,000 | 5,000-30,000 | 100,000 | 5-15 per applicant |
| Personal Statement | 100 | 800-2,000 | 25,000 | One per applicant |
| Languages | 500 | 1,000-5,000 | 10,000 | 1-3 per applicant |
| Parents | 200 | 800-4,000 | 5,000 | 1-2 per applicant |

**Severity:**
- Below min or above max: **ERROR**
- Outside expected range: **WARNING**

#### Numeric Outliers

| Column | Max Reasonable | Max Possible | Special Checks |
|--------|----------------|--------------|----------------|
| `Exp_Hour_Total` | 10,000 | 50,000 | Unit check (minutes vs hours) |
| `Exp_Hour_Research` | 5,000 | 20,000 | - |
| `Age` | 40 | 70 | Min: 18 |
| `GPA` | 4.5 | 4.5 | Scale detection (4.0 vs 5.0) |
| `Parent_Education` | 6 | 6 | Ordinal encoding check |

**Unit Mismatch Detection:**
- If `median(Exp_Hour_Total) > 10,000`: ERROR - likely in minutes, not hours
- If `mean(Exp_Hour_Total) > 20,000`: WARNING - verify units

**GPA Scale Detection:**
- If `max(GPA) > 4.5`: WARNING - using 5.0 scale instead of 4.0

#### Cross-File Consistency

**Referential Integrity:**
1. Every `Amcas_ID` in auxiliary files MUST exist in Applicants → ERROR if violated
2. Coverage checks:
   - Experiences: 95% of applicants should have records → WARNING if <95%
   - Personal Statement: 99% coverage expected → WARNING if <99%
   - Secondary Application: 70% coverage (not all complete) → WARNING if <70%

**Row Count Ratios:**
- Experiences: 3-15 per applicant (avg) → WARNING if outside range
- Languages: 1-3 per applicant → WARNING if outside range
- Parents: 1-2 per applicant → WARNING if outside range

#### Missing Value Patterns

| Scenario | Severity | Threshold |
|----------|----------|-----------|
| Critical column >50% missing | ERROR | e.g., `Amcas_ID`, `Age`, `Exp_Hour_Total` |
| Required column >20% missing | WARNING | Most feature columns |
| Optional column >70% missing | INFO | These get dropped anyway |
| Entire column all NaN | WARNING | Suggests export issue |
| >50% of rows missing >50% of columns | WARNING | Truncation detected |

#### Duplicate Detection

| File Type | Duplicate ID Rule | Exact Row Duplicate Rule |
|-----------|-------------------|--------------------------|
| 1-to-1 (Applicants, PS) | ERROR | WARNING |
| 1-to-many (Experiences) | Expected (INFO) | WARNING |

### 4. Feature Drift Detection

**Statistical Tests:**

| Feature Type | Test | Significance | Effect Size Threshold | Drift Threshold |
|--------------|------|--------------|----------------------|-----------------|
| Numeric | Kolmogorov-Smirnov | p < 0.01 | |Cohen's d| > 0.5 | Large effect |
| Categorical | Chi-square | p < 0.01 | Cramér's V > 0.3 | Medium-large effect |

**Severity Thresholds:**
- **>30% features drifted**: ERROR - model may not be applicable, consider retraining
- **10-30% features drifted**: WARNING - monitor predictions, may need recalibration
- **<10% features drifted**: INFO - expected natural variation

**High-Risk Features for Drift Monitoring:**
```python
DRIFT_SENSITIVE_FEATURES = [
    "Exp_Hour_Total",           # Core experience metric
    "Exp_Hour_Research",        # Research commitment
    "Exp_Hour_Volunteer_Med",   # Service orientation
    "First_Generation_Ind",     # Demographic shift indicator
    "Disadvantaged_Ind",        # SES shift indicator
    "writing_quality",          # Rubric quality (if available)
    "mission_alignment_service_orientation",  # Mission fit
]
```

**Binary Feature Anomaly Detection:**
- Feature always 0 in training, now >5% positive: **WARNING**
- Balanced feature (20-80%) becomes extreme (<5% or >95%): **WARNING**

### 5. Year-Over-Year Schema Changes

**Schema Change Categories:**

| Change Type | Detection | Severity | Handling |
|-------------|-----------|----------|----------|
| Column added | New col in new data | INFO | Ignore (don't use in model) |
| Column removed | Missing from new data | ERROR (if critical), WARNING (if optional) | Check REQUIRED_COLUMNS |
| Column renamed | Fuzzy match | INFO/WARNING | Use mapping, log change |
| Data type changed | `dtype` comparison | WARNING | Convert if possible, error if incompatible |
| Coding scheme changed | Value set comparison | WARNING/ERROR | Remap if possible |

**Coding Scheme Detection:**

```python
Binary schemes: {"Yes", "No"}, {"Y", "N"}, {1, 0}, {True, False}
→ If changed (e.g., Yes/No → Y/N): WARNING, but can be auto-converted

Ordinal schemes: Consecutive integers (0-N)
→ If range changes (0-5 → 0-6): WARNING, check mapping

Categorical: Text labels
→ If new categories appear: INFO, handle as unknown category
```

**Special Case: Parent Education Categories**

If new education levels appear that aren't in `PARENT_EDUCATION_MAP`:
- **Severity**: WARNING
- **Handling**: Map to default (ordinal 2 = "Some college") or median
- **Action Required**: Admin must review and update mapping

### 6. File-Specific Validation

#### Experiences File

```python
def validate_experiences_file(df, applicant_ids):
    checks = [
        # Experience count per applicant
        - <3 experiences: WARNING (may be incomplete)
        - >50 experiences: WARNING (possible duplicates)

        # Hour validation
        - Total_Hours > 50,000: ERROR (unit mismatch?)
        - Median > 10,000: ERROR (likely minutes not hours)

        # Date logic
        - Start_Date > End_Date: ERROR

        # Experience types
        - Unknown Exp_Type: INFO (new category)
    ]
```

#### Personal Statement File

```python
def validate_personal_statement_file(df):
    checks = [
        # Text presence
        - Missing personal_statement column: ERROR
        - Blank statements: WARNING

        # Length validation
        - >5,300 characters: WARNING (AMCAS limit exceeded)
        - >10% at exactly 5,000 chars: WARNING (truncation suspected)

        # Distribution
        - Median length: INFO (log for monitoring)
    ]
```

#### GPA Trend File

```python
def validate_gpa_trend_file(df):
    checks = [
        # Scale detection
        - GPA > 5.0: ERROR (exceeds all known scales)
        - GPA > 4.5: WARNING (5.0 scale instead of 4.0?)
        - GPA < 0.0: ERROR (negative GPA invalid)

        # Trend categories
        - Unknown trend category: WARNING (update GPA_TREND_MAP)
    ]
```

#### Parents File

```python
def validate_parents_file(df):
    checks = [
        # Record count
        - >2 parents per applicant: WARNING (duplicates?)

        # Education levels
        - Unknown education level: WARNING (update PARENT_EDUCATION_MAP)
    ]
```

### 7. Edge Cases in Score-Only Path

#### New Columns in Scoring Data

**Scenario:** New cycle adds essay prompt → new column in Secondary Application

**Handling:**
```python
new_cols = set(new_df.columns) - set(training_features)
# Result: INFO message, columns ignored by model
```

**Rule:** New columns are informational only, never cause errors

#### Binary Feature Always-Zero → Now-Positive

**Scenario:** `Military_Service` was 0% in 2022-2023, now 10% in 2024

**Detection:**
```python
if train_mean == 0 and new_mean > 0.05:
    severity = WARNING
    message = f"{feature}: was always 0 in training, now {new_mean*100:.1f}% positive"
```

**Implications:**
- Model has never seen this feature = 1
- Predictions for these applicants may be unreliable
- Consider Plan A (structured only) if rubric unavailable

#### Rubric Scores Missing for All Applicants

**Scenario:** New cycle hasn't been manually scored yet

**Detection:**
```python
rubric_coverage = df[rubric_features].notna().any(axis=1).mean()

if rubric_coverage == 0.0:
    recommendation = "Use Plan A model (structured features only)"
    severity = INFO

elif rubric_coverage < 0.5:
    recommendation = "Use Plan A model (insufficient rubric coverage)"
    severity = WARNING

else:
    recommendation = "Use Plan B model (rubric + structured)"
    severity = SUCCESS
```

**Model Selection:**
- 0% rubric coverage → **Plan A** (structured only)
- 1-50% coverage → **Plan A** (safer choice)
- 51-100% coverage → **Plan B** (structured + rubric)

#### Experience Hours 10x Higher

**Scenario:** Data export changed from hours to minutes

**Detection:**
```python
median_hours = df["Exp_Hour_Total"].median()

if median_hours > 10000:
    severity = ERROR
    message = "Median hours suggests minutes instead of hours (divide by 60?)"
    recommendation = "Convert minutes to hours before proceeding"
```

**Automatic Fix:** Could offer one-click "Divide by 60" button in UI

---

## Implementation Recommendations

### Phase 1: Critical Validations (Week 1)

**Priority 1 - Blocking Errors:**
1. ID column fuzzy matching
2. Row count validation (min/max thresholds)
3. Cross-file consistency (orphaned IDs)
4. Critical columns >50% missing
5. Numeric hard limits (age, GPA, hours)

**Code Structure:**
```python
# pipeline/validation/__init__.py
from .id_column import validate_id_column
from .row_counts import validate_row_count
from .consistency import validate_cross_file_consistency
from .missing_values import validate_missing_values
from .numeric_ranges import validate_numeric_ranges

# pipeline/validation/orchestrator.py
def validate_uploaded_data(files, mode="auto") -> ValidationResult:
    result = ValidationResult()

    # Run critical checks first
    for file_type, df in files.items():
        id_check = validate_id_column(df, file_type)
        if id_check["status"] == "ERROR":
            result.add_error(id_check)
            return result  # Fail fast

    # Continue with other checks...
    return result
```

### Phase 2: Quality Warnings (Week 2)

**Priority 2 - Non-Blocking Warnings:**
1. Column count validation
2. Outlier detection (IQR method)
3. Missing value patterns
4. Duplicate detection
5. File-specific validation (Experiences, PS, GPA, Parents)

**User Experience:**
- Display warnings in UI with "Continue Anyway" option
- Require checkbox acknowledgment before proceeding
- Log warnings for audit trail

### Phase 3: Advanced Analytics (Week 3)

**Priority 3 - Drift Detection:**
1. Distribution comparison (KS test, Chi-square)
2. Binary feature anomaly detection
3. High-risk feature drift monitoring
4. Schema evolution detection
5. Rubric availability check → model selection

**Caching Strategy:**
```python
# Cache reference distributions from training data
CACHE_DIR / "reference_distributions.pkl"

reference_distributions = {
    "Exp_Hour_Total": {
        "mean": 1500.0,
        "std": 800.0,
        "median": 1300.0,
        "p25": 900.0,
        "p75": 1900.0,
    },
    # ... other features
}
```

### Phase 4: Testing & Refinement (Week 4)

**Testing Strategy:**

```python
# tests/test_validation.py
import pytest
from pipeline.validation import validate_uploaded_data

def test_valid_2024_data():
    """Test that 2024 data passes validation."""
    files = load_2024_data()
    result = validate_uploaded_data(files, mode="scoring")
    assert result.can_proceed == True
    assert len(result.errors) == 0

def test_missing_id_column():
    """Test that missing ID column is caught."""
    df = pd.DataFrame({"wrong_column": [1, 2, 3]})
    result = validate_id_column(df, "applicants")
    assert result["status"] == "ERROR"

def test_unit_mismatch_detection():
    """Test that minutes/hours mismatch is detected."""
    df = pd.DataFrame({
        "Amcas_ID": [1, 2, 3],
        "Exp_Hour_Total": [18000, 20000, 22000]  # Clearly in minutes
    })
    result = validate_numeric_ranges(df)
    assert any("minutes" in error for error in result["findings"]["errors"])

def test_binary_feature_drift():
    """Test drift detection for binary features."""
    train_df = pd.DataFrame({"feature": [0] * 1000})  # Always 0
    new_df = pd.DataFrame({"feature": [1] * 100 + [0] * 900})  # Now 10%
    result = validate_binary_prevalence_shift(train_df, new_df, ["feature"])
    assert len(result["findings"]["warnings"]) > 0
```

### Configuration Management

**Store thresholds in config:**

```python
# pipeline/validation_config.py
VALIDATION_THRESHOLDS = {
    "row_counts": {
        "applicants": {"min": 100, "expected": (800, 2000), "max": 25000},
    },
    "outliers": {
        "iqr_multiplier": 1.5,  # Standard IQR outlier detection
        "warning_percentage": 0.05,  # Warn if >5% outliers
    },
    "drift": {
        "numeric_effect_size": 0.5,  # Cohen's d threshold
        "categorical_effect_size": 0.3,  # Cramér's V threshold
        "p_value": 0.01,
        "error_percentage": 0.30,  # >30% features → ERROR
        "warning_percentage": 0.10,  # >10% features → WARNING
    },
    "missing_values": {
        "critical_threshold": 0.50,  # >50% missing → ERROR
        "required_threshold": 0.20,  # >20% missing → WARNING
    },
}
```

**Allow override via environment:**

```python
import os

VALIDATION_THRESHOLDS["drift"]["error_percentage"] = float(
    os.environ.get("DRIFT_ERROR_THRESHOLD", "0.30")
)
```

---

## API Integration

### Validation Endpoint

```python
# api/routes/validation.py
from fastapi import APIRouter, UploadFile, File
from pipeline.validation import validate_uploaded_data

router = APIRouter()

@router.post("/validate")
async def validate_files(
    applicants: UploadFile = File(...),
    experiences: UploadFile = File(...),
    personal_statement: UploadFile = File(...),
    # ... other files
):
    """
    Validate uploaded AMCAS data files.

    Returns:
        {
            "overall_status": "error" | "warning" | "success",
            "can_proceed": bool,
            "data_mode": "training" | "scoring" | "mixed",
            "summary": {
                "error_count": int,
                "warning_count": int,
                "info_count": int
            },
            "errors": [...],
            "warnings": [...],
            "info": [...]
        }
    """
    # Load files
    files = {
        "applicants": pd.read_excel(applicants.file),
        "experiences": pd.read_excel(experiences.file),
        "personal_statement": pd.read_excel(personal_statement.file),
        # ... load other files
    }

    # Validate
    result = validate_uploaded_data(files)

    return result.to_dict()
```

### UI Integration

**Frontend Flow:**

```typescript
// 1. Upload files
const files = {
  applicants: applicantsFile,
  experiences: experiencesFile,
  personalStatement: personalStatementFile,
  // ...
};

// 2. Validate
const validationResult = await api.validateFiles(files);

// 3. Show results
if (validationResult.overall_status === "error") {
  // Block UI, show errors
  showErrorModal(validationResult.errors);
} else if (validationResult.overall_status === "warning") {
  // Show warnings, require acknowledgment
  showWarningModal(validationResult.warnings, {
    onAcknowledge: () => proceedToPipeline(),
    onCancel: () => returnToUpload(),
  });
} else {
  // Success, proceed
  proceedToPipeline();
}
```

---

## Monitoring & Observability

### Validation Metrics to Track

```python
# Log to monitoring system
validation_metrics = {
    "timestamp": datetime.utcnow(),
    "file_upload_id": upload_id,
    "data_mode": result.data_mode.value,
    "overall_status": result.overall_status.value,
    "error_count": len(result.errors),
    "warning_count": len(result.warnings),
    "row_count": len(uploaded_files["applicants"]),
    "feature_drift_percentage": drift_summary.get("drifted_count", 0) / total_features,
    "rubric_coverage": rubric_coverage,
    "processing_time_seconds": elapsed_time,
}

log_to_datadog(validation_metrics)
```

### Alerting Thresholds

- **Error rate >10%**: Alert admissions team
- **Severe drift detected**: Alert ML team
- **Schema change detected**: Alert engineering team
- **Upload volume spike**: Alert operations team

---

## Success Criteria

### Validation System Should:

1. **Prevent bad data from entering pipeline**: 0 instances of corrupted predictions due to data quality
2. **Handle schema evolution gracefully**: Support year-over-year AMCAS changes without code updates
3. **Provide actionable feedback**: Non-technical staff can understand and fix issues
4. **Minimize false positives**: <5% of valid uploads blocked or warned incorrectly
5. **Fast validation**: Complete in <30 seconds for typical upload (17K applicants)

### Performance Targets

- **Validation latency**: <30 seconds for full validation
- **False positive rate**: <5% (valid data flagged as warning)
- **False negative rate**: <1% (bad data passes validation)
- **Schema change detection**: 100% of column renames caught
- **Drift detection recall**: >90% of significant distribution shifts detected

---

## Next Steps

1. **Review with stakeholders**: Validate thresholds with admissions team
2. **Implement Phase 1**: Critical validations (blocking errors)
3. **Test with historical data**: Run validation on 2022-2024 data
4. **Tune thresholds**: Adjust based on false positive/negative rates
5. **Implement Phase 2-3**: Warnings and drift detection
6. **User acceptance testing**: Train staff on validation UI
7. **Deploy to production**: Gradual rollout with monitoring

---

## Appendix: Quick Reference

### Validation Status Codes

- **ERROR**: Blocks pipeline execution
- **WARNING**: Requires user acknowledgment to proceed
- **INFO**: Informational only, does not block
- **SUCCESS**: All checks passed

### Common Validation Failures & Fixes

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| "No ID column found" | Column renamed in new export | Check file structure, contact AMCAS |
| "X applicants have duplicate records" | Export issue or manual data entry | Remove duplicates in Applicants file |
| "Median hours suggests minutes" | AMCAS changed units | Divide experience hours by 60 |
| "Severe feature drift" | Demographics changed or data quality | Review distributions, consider model retrain |
| "Missing required files" | Incomplete upload | Upload all 7 required files |
| "Orphaned IDs in Experiences" | Mismatch between files | Ensure all files from same export cycle |

### Threshold Tuning Guide

After initial deployment, monitor these metrics and adjust thresholds:

1. **False positive rate**: If >10% of valid uploads get warnings, increase warning thresholds
2. **False negative rate**: If bad data passes validation, tighten error thresholds
3. **Drift sensitivity**: If too many false drift alerts, increase effect size thresholds
4. **Row count ranges**: Update expected ranges based on actual upload volumes

---

**Document Version**: 1.0
**Last Updated**: 2026-02-13
**Author**: Data Science Team
**Status**: Ready for Implementation
