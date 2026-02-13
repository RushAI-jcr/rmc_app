---
title: "refactor: Rewrite Data Preparation Pipeline"
type: refactor
date: 2026-02-13
---

# Rewrite Data Preparation Pipeline

## Overview

Replace the 4 scattered data pipeline files (`data_ingestion.py`, `data_cleaning.py`, `feature_engineering.py`, `run_pipeline.py`) with a clean, consolidated implementation that:

1. Reads all 12 xlsx files per year from `data/raw/`
2. Normalizes column names and IDs across years
3. Aggregates multi-row tables, joins to applicants
4. Cleans and imputes missing values
5. Engineers structured + composite + rubric features
6. Produces train/test splits ready for model training
7. Works identically for historical batch training AND production API scoring of new uploads

## Problem Statement

The current pipeline has code spread across 4 files with interleaved responsibilities, making it hard to maintain and extend. Key issues:

- **Data leakage**: Imputation statistics (age median, missingness thresholds) are computed on the full dataset before the temporal train/test split. The rewrite must fit on train-only, then transform test and scoring data.
- **Scattered logic**: Column normalization happens in `data_ingestion.py`, typo fixes in `data_cleaning.py`, and alias handling in `feature_engineering.py`. All should live together.
- **No transformation persistence**: Fitted imputation values and feature column lists aren't saved, so the scoring pipeline can't apply identical transformations to new data.
- **Dual-mode complexity**: The `file_map` parameter is threaded through every function individually rather than being a clean mode switch.

## Proposed Solution

Replace with 3 new files + update 1 existing file:

| File | Purpose | Replaces |
|------|---------|----------|
| `pipeline/data_preparation.py` | Ingest, normalize, join, clean, impute | `data_ingestion.py` + `data_cleaning.py` |
| `pipeline/feature_engineering.py` | Extract features, engineer composites, load rubric, combine | Rewrite of existing `feature_engineering.py` |
| `pipeline/run_pipeline.py` | CLI orchestrator with train/test split | Rewrite of existing `run_pipeline.py` |
| `pipeline/score_pipeline.py` | Update imports to use new modules | Update only |

### Architecture

```
                        ┌──────────────────┐
                        │   config.py      │  (unchanged - all constants stay here)
                        └────────┬─────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                     ▼
  ┌──────────────────┐ ┌──────────────────┐  ┌──────────────────┐
  │data_preparation.py│ │feature_engineering│  │  run_pipeline.py │
  │                  │ │       .py        │  │                  │
  │ • read xlsx      │ │ • structured     │  │ • CLI entry point│
  │ • normalize cols │ │ • composites     │  │ • temporal split │
  │ • normalize IDs  │ │ • rubric loader  │  │ • leakage-safe   │
  │ • aggregate      │ │ • combine sets   │  │ • progress cb    │
  │ • join           │ │ • fit/transform  │  │ • save artifacts │
  │ • clean/impute   │ │   pattern        │  │                  │
  └──────────────────┘ └──────────────────┘  └──────────────────┘
            │                    │                     │
            ▼                    ▼                     ▼
  ┌──────────────────────────────────────────────────────────┐
  │              score_pipeline.py (updated imports)          │
  │  Production path: load saved artifacts → transform →     │
  │  score new applicants                                    │
  └──────────────────────────────────────────────────────────┘
```

## Technical Approach

### Phase 1: `data_preparation.py` — Ingest, Normalize, Join, Clean

This file consolidates all raw data loading into a single module.

#### Functions to implement:

```python
# data_preparation.py

def prepare_dataset(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
    progress_callback: Callable[[str, int], None] | None = None,
) -> pd.DataFrame:
    """Main entry point. Returns one-row-per-applicant DataFrame.

    Stages:
      1. Load all xlsx files (per year or from file_map)
      2. Normalize columns and IDs
      3. Aggregate multi-row tables
      4. Left-join everything to Applicants on Amcas_ID
      5. Clean: drop high-missingness cols, impute NaNs
      6. Normalize binary Yes/No → 0/1

    Returns unified DataFrame with app_year column.
    """
```

#### Key design decisions:

1. **Single file_map mode detection**: If `file_map` is provided, treat as single-cycle API mode. Otherwise, iterate year folders.

2. **Column normalization** — consolidated in one place:
   - Strip whitespace, `" "` → `"_"`, remove `(` and `)`
   - ID column: check `ID_ALIASES` list, rename to `Amcas_ID`
   - Typo fix: `Disadvantanged_Ind` → `Disadvantaged_Ind`
   - Schools filename variation: handled in `_read_xlsx` via config

3. **Aggregation functions** (preserve existing logic from `data_ingestion.py`):
   - `_aggregate_languages(df)` → count per applicant
   - `_aggregate_parents(df)` → max education ordinal via `PARENT_EDUCATION_MAP`
   - `_aggregate_gpa_trend(df)` → ordinal via `GPA_TREND_MAP`
   - `_derive_experience_flags(df)` → 9 binary flags via `EXP_TYPE_TO_FLAG`

4. **Cleaning** — moved into same module (currently in `data_cleaning.py`):
   - Drop columns in `COLUMNS_TO_DROP` (>70% missing)
   - Impute hours → 0, percentages → 0, Age → median
   - Log all transformations

5. **No feature engineering here** — this module outputs the cleaned, joined DataFrame. Feature extraction happens in the next module.

#### Files to delete after rewrite:
- `pipeline/data_ingestion.py` (437 lines → merged into `data_preparation.py`)
- `pipeline/data_cleaning.py` (82 lines → merged into `data_preparation.py`)

---

### Phase 2: `feature_engineering.py` — Rewrite with Fit/Transform Pattern

The key improvement: introduce a **fit/transform pattern** so fitted statistics (medians, column lists) are persisted and reusable for scoring new data.

#### Functions to implement:

```python
# feature_engineering.py

class FeaturePipeline:
    """Fit on training data, transform any dataset consistently.

    Attributes:
        numeric_medians_: dict[str, float]  — imputation values for numeric features
        feature_columns_: list[str]         — ordered feature column names
        rubric_medians_: dict[str, float]   — imputation values for rubric zero-as-missing
    """

    def fit(self, df: pd.DataFrame) -> "FeaturePipeline":
        """Fit on training data only. Learns imputation values."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply fitted transformations. Returns feature matrix with Amcas_ID."""

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convenience: fit + transform in one call."""

    def save(self, path: Path) -> None:
        """Persist fitted state to disk (joblib)."""

    @classmethod
    def load(cls, path: Path) -> "FeaturePipeline":
        """Load previously fitted pipeline."""
```

#### Transform steps (inside `transform()`):

1. **Extract structured features** — 11 numeric + 10 binary from config lists
2. **Engineer composites** — 7 features (volunteer hours, clinical hours, adversity count, grit index, experience diversity, community ratio, direct care ratio)
3. **Load rubric features** — from `rubric_scores.json`, collapse 30 → 14, impute zeros with fitted medians
4. **Combine** — merge all feature sets on `Amcas_ID`
5. **Final NaN sweep** — fill any remaining NaN with 0

#### Data leakage fix:

```python
# BEFORE (current code — leaks test info):
df = build_unified_dataset()          # all years
df = clean_dataset(df)                # impute age with median of ALL years
structured = extract_structured_features(df)  # fillna(0) on ALL years

# AFTER (new code — train-only fitting):
df = prepare_dataset()                        # all years, basic cleaning only
train_df = df[df["app_year"].isin([2022, 2023])]
test_df = df[df["app_year"] == 2024]

pipeline = FeaturePipeline()
X_train = pipeline.fit_transform(train_df)    # fit medians on TRAIN only
X_test = pipeline.transform(test_df)          # apply TRAIN medians to test
pipeline.save(MODELS_DIR / "feature_pipeline.joblib")
```

#### What stays the same:

- All feature names, formulas, and mappings from `config.py` are unchanged
- Binary flag derivation logic from experiences is preserved
- Rubric score loading and 30→14 collapse logic is preserved
- `DEMOGRAPHICS_FOR_FAIRNESS_ONLY` guard is preserved

---

### Phase 3: `run_pipeline.py` — Clean Orchestrator

Rewrite the CLI entry point to use the new modules with a clear, linear flow.

```python
# run_pipeline.py

def run(
    skip_ingestion: bool = False,
    skip_rubric: bool = False,
    two_stage: bool = False,
    bakeoff: bool = False,
) -> None:
    """Full pipeline: ingest → features → split → train → evaluate → audit."""

    # Step 1: Data preparation
    if skip_ingestion:
        df = _load_from_processed_csvs()
    else:
        df = prepare_dataset()
        _save_master_csvs(df)

    # Step 2: Temporal split (BEFORE feature engineering to prevent leakage)
    train_df = df[df["app_year"].isin(TRAIN_YEARS)]
    test_df = df[df["app_year"] == TEST_YEAR]

    # Step 3: Feature engineering (fit on train, transform both)
    feature_pipe = FeaturePipeline(include_rubric=not skip_rubric)
    X_train_df = feature_pipe.fit_transform(train_df)
    X_test_df = feature_pipe.transform(test_df)
    feature_pipe.save(MODELS_DIR / "feature_pipeline.joblib")

    # Step 4: Extract arrays for sklearn
    feature_cols = feature_pipe.feature_columns_
    X_train = X_train_df[feature_cols].values
    X_test = X_test_df[feature_cols].values
    y_train_score = train_df.set_index(ID_COLUMN).loc[X_train_df[ID_COLUMN], TARGET_SCORE].values
    y_test_score = test_df.set_index(ID_COLUMN).loc[X_test_df[ID_COLUMN], TARGET_SCORE].values
    # ... bucket labels similarly

    # Step 5+: Model training, evaluation, fairness audit (unchanged)
    # ... calls to model_training.py, model_evaluation.py, fairness_audit.py
```

#### Key changes from current `run_pipeline.py`:

1. **Split happens BEFORE feature engineering** — eliminates data leakage
2. **FeaturePipeline class** replaces 5 separate function calls
3. **Artifacts saved** — `feature_pipeline.joblib` persists fitted state
4. **Simpler flow** — no more Plan A/Plan B parallel paths in the orchestrator (the `include_rubric` flag handles this)

---

### Phase 4: Update `score_pipeline.py`

Update the production scoring path to use new modules:

```python
# score_pipeline.py (updated)

def score_new_cycle(
    data_dir: Path,
    cycle_year: int,
    model_pkl: str = "results_A_Structured.pkl",
    file_map: dict[str, Path] | None = None,
    progress_callback: ProgressCallback | None = None,
    rubric_scores_path: Path | None = None,
) -> dict:
    cb = progress_callback or (lambda s, p: None)

    # Step 1: Prepare data (new module)
    cb("ingestion", 10)
    df = prepare_dataset(
        years=[cycle_year],
        data_dir=data_dir,
        file_map=file_map,
    )

    # Step 2: Load fitted feature pipeline (from training)
    cb("features", 40)
    feature_pipe = FeaturePipeline.load(MODELS_DIR / "feature_pipeline.joblib")
    X_df = feature_pipe.transform(df)

    # Step 3: Score with pre-trained model
    cb("ml_scoring", 70)
    # ... load model, predict, assign tiers

    cb("triage", 100)
    return result
```

## Acceptance Criteria

### Functional Requirements

- [x] `data_preparation.py` loads all 12 xlsx file types across 2022-2024
- [x] Column normalization handles all known variations (typos, spaces, case)
- [x] Aggregation produces identical results to current pipeline (same row counts, same feature values)
- [x] `FeaturePipeline.fit()` computes statistics on training data only
- [x] `FeaturePipeline.transform()` applies fitted statistics without leaking test info
- [x] `FeaturePipeline.save()/load()` round-trips correctly
- [x] `run_pipeline.py` produces X_train/X_test/y_train/y_test identical to current pipeline (modulo the leakage fix)
- [x] `score_pipeline.py` works with uploaded files via `file_map`
- [x] Progress callbacks fire at correct milestones
- [x] Protected attributes (Gender, Age, Race, Citizenship) never appear in feature matrices
- [x] All existing config constants (`NUMERIC_FEATURES`, `BINARY_FEATURES`, etc.) are used unchanged

### Non-Functional Requirements

- [x] Logging at every major step (file loads, aggregation counts, imputation counts, feature counts)
- [x] Type hints on all public functions
- [x] Docstrings on all public functions
- [x] No new dependencies beyond what's in `requirements.txt`

### Quality Gates

- [x] Old files deleted: `data_ingestion.py`, `data_cleaning.py`
- [x] `feature_engineering.py` fully rewritten (no leftover functions)
- [x] `run_pipeline.py` fully rewritten
- [x] `score_pipeline.py` updated to use new imports
- [ ] Pipeline runs end-to-end: `python -m pipeline.run_pipeline` (blocked by `shap` dependency, not part of this refactor)
- [ ] Pipeline runs with `--skip-rubric`, `--two-stage`, `--bakeoff` flags (blocked by `shap` dependency)

## Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| Aggregation logic differs after rewrite | Compare master CSVs row-by-row against existing `data/processed/master_*.csv` |
| Data leakage fix changes model metrics | Expected — document the before/after metrics. Leakage-free is correct. |
| `score_pipeline.py` breaks | Test API scoring path with sample file_map after rewrite |
| `two_stage_pipeline.py` breaks | It consumes the split dict from `run_pipeline.py` — same interface preserved |
| Rubric scores JSON format changes | No format change — same `data/cache/rubric_scores.json` |

## References

### Internal References
- [pipeline/config.py](pipeline/config.py) — all constants, feature lists, paths (434 lines, unchanged)
- [pipeline/data_ingestion.py](pipeline/data_ingestion.py) — current ingestion (437 lines, to be replaced)
- [pipeline/data_cleaning.py](pipeline/data_cleaning.py) — current cleaning (82 lines, to be replaced)
- [pipeline/feature_engineering.py](pipeline/feature_engineering.py) — current features (264 lines, to be rewritten)
- [pipeline/run_pipeline.py](pipeline/run_pipeline.py) — current orchestrator (269 lines, to be rewritten)
- [pipeline/score_pipeline.py](pipeline/score_pipeline.py) — production scoring (to be updated)
- [pipeline/model_training.py](pipeline/model_training.py) — model training (398 lines, unchanged)

### Data Quality Documentation
- [data/raw/raw_data_audit.md](data/raw/raw_data_audit.md) — comprehensive row/column audit
- [docs/brainstorms/data_validation_specification.md](docs/brainstorms/data_validation_specification.md) — validation rules
- [docs/brainstorms/validation_implementation_summary.md](docs/brainstorms/validation_implementation_summary.md) — implementation guidance

### Related Plans
- [docs/plans/2026-02-13-feat-two-stage-screening-model-plan.md](docs/plans/2026-02-13-feat-two-stage-screening-model-plan.md) — two-stage model consuming this pipeline's output
- [docs/plans/2026-02-13-feat-amcas-ingestion-ui-plan.md](docs/plans/2026-02-13-feat-amcas-ingestion-ui-plan.md) — API upload flow that calls `score_pipeline.py`
