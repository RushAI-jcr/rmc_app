# v1 → v2 Rubric Scorer Migration - Completed

**Date**: 2026-02-13
**Status**: Phase 1 Complete (architectural consolidation)

## Summary

Successfully migrated the LLM rubric scoring pipeline from v1 (composite prompts with halo effects) to v2 (research-grounded atomic prompts).

## Changes Made

### 1. Unified LLM Client ✅

**File**: [pipeline/llm_client.py](../../pipeline/llm_client.py)

- Consolidated two Azure clients (openai SDK, azure-ai-inference SDK) into one
- Added JSON mode enforcement (`response_format={"type": "json_object"}`)
- Added tenacity-based exponential backoff retry (5 attempts, 4-60s waits)
- Added deterministic seed (`seed=42`) for reproducibility
- Removed hardcoded endpoint URLs (now env-only)
- Removed `azure_foundry_client.py` (deprecated)

**Updated**: [.env.example](../../.env.example) — removed Foundry vars, kept only Azure OpenAI

---

### 2. Extracted Shared Data Helpers ✅

**File**: [pipeline/data_ingestion.py](../../pipeline/data_ingestion.py)

Added two new public functions:
- `build_personal_statements_dict(years) -> dict[int, str]` — AMCAS ID → PS text
- `build_secondary_texts_dict(years) -> dict[int, str]` — AMCAS ID → concatenated secondary essays

**Updated**:
- [pipeline/run_rubric_scoring_v1_deprecated.py](../../pipeline/run_rubric_scoring_v1_deprecated.py) — uses shared helpers, marked DEPRECATED
- [pipeline/run_rubric_scoring_v2.py](../../pipeline/run_rubric_scoring_v2.py) — uses shared helpers

**Removed**: Duplicate `_build_personal_statements_dict()` and `_build_secondary_texts_dict()` from both runners

---

### 3. Fixed feature_engineering.py for v2 ✅

**File**: [pipeline/feature_engineering.py](../../pipeline/feature_engineering.py)

`load_rubric_features()` now supports BOTH v1 and v2 JSON formats:

**v1 format** (flat dict):
```json
{
  "13149516": {
    "writing_quality": 4,
    "direct_patient_care_depth": 3,
    ...
  }
}
```

**v2 format** (nested with scores/details/metadata):
```json
{
  "13149516": {
    "scores": {
      "writing_quality": 3,
      "direct_patient_care_depth_and_quality": 4,
      ...
    },
    "details": { ... },
    "metadata": { ... }
  }
}
```

**Auto-detection logic**:
- Inspects first entry structure
- Detects `"scores"` key → v2
- No `"scores"` key → v1

**v2 dimension name mapping**:
- v2 uses `"direct_patient_care_depth_and_quality"`
- v1 uses `"direct_patient_care_depth"`
- Loader maps v2 names → v1-compatible names for `RUBRIC_FEATURES_FINAL`

**Median imputation**:
- v1: median = 3.0 (1-5 scale)
- v2: median = 2.5 (1-4 scale)

---

### 4. Promoted v2 to Production ✅

**Renamed**:
- `pipeline/run_smoke_test_v2.py` → `pipeline/run_rubric_scoring_v2.py`

**Updated**:
- Removed `--client foundry` flag (now uses unified client only)
- Added `--resume` flag to skip already-scored applicants
- Updated docstring with research citations (ACL 2024, EMNLP 2023, arxiv)
- Changed function name: `run_smoke_test()` → `run_scoring()`
- Removed "smoke test" language — this is now the production scorer

**Deprecated**:
- `pipeline/run_rubric_scoring.py` → `pipeline/run_rubric_scoring_v1_deprecated.py`
- Added deprecation notice in docstring
- File preserved only for reference

---

## Remaining Work (Phase 2)

### 5. Update config.py Dimensions (TODO)

**Issue**: `config.py` has three overlapping dimension lists:
- `ALL_RUBRIC_DIMS_V1` (32 dims) — v1 composite scoring
- `ALL_RUBRIC_DIMS_V2` (16 dims) — v2 atomic scoring
- `RUBRIC_FEATURES_FINAL` (15 features) — references v1 names

**Action needed**:
1. Remove `ALL_RUBRIC_DIMS_V1` and all v1-specific constants
2. Update `RUBRIC_FEATURES_FINAL` to use v2 dimension names
3. Ensure `FEATURE_DISPLAY_NAMES` maps v2 names to pretty labels

**Impact**: Model training (if re-run) will use v2 feature names

---

### 6. Add Secondary Essay Scoring to v2 (TODO)

**Issue**: v2's [rubric_prompts_v2.py:506-529](../../pipeline/rubric_prompts_v2.py#L506-L529) has a `SECONDARY_ESSAY_TEMPLATE` but it's never used.

v1 scored 5 secondary dims:
- `personal_attributes_insight`
- `adversity_response_quality`
- `reflection_depth`
- `healthcare_experience_quality`
- `research_depth`

**Action needed**:
1. Add secondary scoring functions to [rubric_scorer_v2.py](../../pipeline/rubric_scorer_v2.py)
2. Build secondary-specific prompts in [rubric_prompts_v2.py](../../pipeline/rubric_prompts_v2.py) (5 atomic prompts)
3. Update `score_applicant()` to call secondary scorer if `secondary_text` is provided

**Impact**: Adds 5 more API calls per applicant (total: up to 21 calls)

---

### 7. Fix score_pipeline.py Feature Column Ordering (TODO)

**Issue**: [score_pipeline.py:158-162](../../pipeline/score_pipeline.py#L158-L162) builds feature matrix as:
```python
X = features_df[feature_cols].values.astype(float)
```

If v2 adds/renames columns, the column order may not match what the model was trained on → silently wrong predictions.

**Action needed**:
1. Load model's expected feature names from pickle (stored during training)
2. Reindex `features_df` to match the model's feature order
3. Raise an error if expected features are missing (not silently default to 0)

Example fix:
```python
model_feature_names = model_data["feature_names"]  # saved during training
X = features_df.reindex(columns=model_feature_names, fill_value=0).values.astype(float)
```

**Impact**: Prevents silent prediction errors when v2 feature names are used

---

### 8. Additional Cleanup (TODO)

**Files to remove** (after confirming v2 works in production):
- `pipeline/rubric_scorer.py` (v1 scorer, 688 lines)
- `pipeline/run_rubric_scoring_v1_deprecated.py` (deprecated runner)
- `pipeline/azure_foundry_client.py` (replaced by unified client)

**Update git history**:
```bash
git rm pipeline/rubric_scorer.py pipeline/run_rubric_scoring_v1_deprecated.py pipeline/azure_foundry_client.py
```

---

## Testing Checklist

Before deploying v2 to production:

- [ ] Run `python -m pipeline.run_rubric_scoring_v2 --dry-run` to verify prompts
- [ ] Score 10 applicants: `python -m pipeline.run_rubric_scoring_v2 -n 10`
- [ ] Validate output: `python -m pipeline.validate_scores data/cache/rubric_scores_v2.json`
- [ ] Check parse failure rate < 10%
- [ ] Check score distribution (no single level > 40%)
- [ ] Check PS dimension correlations (target: r < 0.60 for all pairs)
- [ ] Test resume mode: run with `--resume`, confirm already-scored applicants are skipped
- [ ] Load v2 scores into feature_engineering: `load_rubric_features(version="v2")`
- [ ] Run score_pipeline with v2 features, verify output

---

## Architecture After Migration

```
# Scoring (v2 atomic prompts, 1-4 scale)
run_rubric_scoring_v2.py ──→ rubric_scorer_v2.py ──→ rubric_prompts_v2.py
                         └──→ llm_client.py (unified Azure OpenAI)
                         └──→ data_ingestion.py (shared PS/secondary helpers)

# Feature Engineering (v1/v2 compatible)
feature_engineering.py ──→ load_rubric_features(version="auto")
                      ├──→ reads rubric_scores.json (v1) OR rubric_scores_v2.json (v2)
                      └──→ auto-detects format, maps v2 dims → v1 names

# ML Scoring (uses feature_engineering output)
score_pipeline.py ──→ feature_engineering.py ──→ RUBRIC_FEATURES_FINAL (v1 names)
                 └──→ XGBoost regressor ──→ triage tiers
```

**Clean boundaries**:
- v1 and v2 share `data_ingestion.py`, `llm_client.py`, `config.py`
- v1 and v2 write different JSON files (`rubric_scores.json` vs `rubric_scores_v2.json`)
- `feature_engineering.py` bridges the two via auto-detection + name mapping

---

## Research Grounding (v2)

v2 scorer is based on these papers:

1. **LLM-Rubric** (ACL 2024, Hashemi et al.): Atomic scoring (1 dimension per call) eliminates halo effects that caused r > 0.97 multicollinearity in v1. Uses 1-4 scale with no neutral midpoint.

2. **AutoSCORE** (arxiv:2509.21910): Evidence extraction before scoring — prompts explicitly ask for `evidence_extracted` field before assigning score.

3. **G-Eval** (EMNLP 2023, Liu et al.): CoT + form-filling paradigm — prompts include evaluation steps and rubric anchors before asking for JSON output.

4. **Rulers** (arxiv:2601.08654): Executable rubrics > prompt engineering alone — prompts include checkbox tests and signal detection guidance.

---

## Contacts

- Architecture questions: See this doc or [pipeline/rubric_prompts_v2.py](../../pipeline/rubric_prompts_v2.py) for research citations
- Deployment: Run `python -m pipeline.run_rubric_scoring_v2 --help` for all flags
- Validation: Use `python -m pipeline.validate_scores <path>` to check output quality
