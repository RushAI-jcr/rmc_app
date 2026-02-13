# Phase 2 v1→v2 Migration Implementation Plan

**Created**: 2026-02-13
**Phase 1 Status**: ✅ Complete (architectural consolidation)
**Phase 2 Status**: 📋 Ready for implementation

## Quick Start

Execute tasks in this order:

1. ✅ **TASK 2** — Add backward compatibility mapping (prevents breaking existing code)
2. **TASK 1** — Add secondary essay scoring to v2 (5 new dimensions)
3. **TASK 3** — Clean up config.py (remove deprecated v1 constants)
4. **TASK 4** — Fix feature column ordering in score_pipeline.py

---

## TASK 1: Add Secondary Essay Scoring to v2

**Status**: Not started
**Impact**: Adds 5 API calls per applicant (7 PS + 5 secondary + 9 exp = 21 total)
**Files**: `rubric_prompts_v2.py`, `rubric_scorer_v2.py`

### Why This Matters

v2 currently skips secondary essay scoring. The trained model expects `personal_attributes_insight` from secondary essays, but v2 doesn't score it. This means the model gets imputed values (median = 3.0) instead of real scores.

### Implementation Steps

See [full plan document](2026-02-13-phase2-implementation-plan.md#task-1-add-secondary-essay-scoring-to-v2) for detailed code changes.

**Key changes**:
- Add `SECONDARY_DIMENSIONS` dict to `rubric_prompts_v2.py` (5 atomic prompts)
- Add `score_all_secondary_essays()` to `rubric_scorer_v2.py`
- Integrate secondary scoring into `score_applicant()` function

**Testing**:
```bash
python -m pipeline.run_rubric_scoring_v2 -n 3
# Should score 21 dimensions per applicant (7 PS + 5 secondary + 9 exp)
```

---

## TASK 2: Add Backward Compatibility Mapping ✅

**Status**: Complete
**Impact**: Allows v2 scores to work with models trained on v1 dimension names
**Files**: `config.py`, `feature_engineering.py`

### Why This Matters

The trained model expects v1 dimension names (`direct_patient_care_depth`), but v2 uses different names (`direct_patient_care_depth_and_quality`). Without mapping, the model gets zeros for all v2 dimensions.

### What Was Done

Added `V2_TO_V1_DIMENSION_MAP` in `config.py` to translate:
- v2: `direct_patient_care_depth_and_quality` → v1: `direct_patient_care_depth`
- v2: `clinical_exposure_depth_and_quality` → v1: `shadowing_depth`
- etc.

Updated `feature_engineering.py` to:
- Auto-detect v1 vs v2 JSON format
- Map v2 dimension names → v1 names when building features
- Handle nested v2 structure: `{scores: {...}, details: {...}, metadata: {...}}`

**Testing**:
```python
from pipeline.feature_engineering import FeaturePipeline
from pipeline.config import CACHE_DIR
import pandas as pd

pipe = FeaturePipeline(include_rubric=True, rubric_path=CACHE_DIR / 'rubric_scores_v2.json')
df = pd.DataFrame({'Amcas_ID': [13149516]})
pipe.fit(df)
features = pipe.transform(df)
print(features.columns.tolist())  # Should include v1 dimension names
```

---

## TASK 3: config.py Cleanup

**Status**: Not started
**Impact**: Removes deprecated v1 constants, adds v2 secondary dimensions
**Files**: `config.py`

### Why This Matters

v1 constants (`ALL_RUBRIC_DIMS_V1`, `PS_DIMS_V1`, etc.) are no longer used but still clutter the config. Marking them as deprecated clarifies which constants to use.

### Implementation Steps

1. Add deprecation comments to v1 constants (lines 216-263)
2. Add `SECONDARY_DIMS_V2` to config.py
3. Update `ALL_RUBRIC_DIMS_V2` to include secondary dimensions
4. Add clarifying comment to `RUBRIC_FEATURES_FINAL`

**Testing**:
```bash
python3 -c "from pipeline.config import ALL_RUBRIC_DIMS_V2, RUBRIC_FEATURES_FINAL; print('v2 dims:', len(ALL_RUBRIC_DIMS_V2)); print('model features:', len(RUBRIC_FEATURES_FINAL))"
```

---

## TASK 4: Fix Feature Column Ordering

**Status**: Not started
**Impact**: Prevents silent prediction errors when feature columns are reordered
**Files**: `score_pipeline.py`, model training code

### Why This Matters

XGBoost models are sensitive to feature order. If `score_pipeline.py` passes features in a different order than the model was trained on, predictions will be silently wrong.

### Implementation Steps

1. Update training code to save `feature_names` in model pickle
2. Update `score_pipeline.py` to load expected feature names from model
3. Reorder feature columns to match model's expected order
4. Raise error if expected features are missing

**Testing**:
```python
from pipeline.score_pipeline import score_new_cycle
from pathlib import Path

result = score_new_cycle(
    data_dir=Path('/Users/JCR/Desktop/rmc_every/data/raw/2024'),
    cycle_year=2024,
    model_pkl='results_D_Struct+Rubric.pkl'
)
print('Scored:', result['applicant_count'], 'applicants')
```

---

## Critical Risks & Mitigations

### Risk 1: Scale Mismatch (v1 uses 1-5, v2 uses 1-4)

**Impact**: Model trained on 1-5 scale receives 1-4 inputs → incorrect predictions

**Mitigation Options**:
1. **Scale v2 scores to v1 range** (quick fix):
   ```python
   # In feature_engineering.py
   if self._rubric_format == "v2":
       row[v1_dim] = (raw_val - 1) * (4/3) + 1  # Maps [1,4] → [1,5]
   ```
2. **Retrain model on v2 scores** (proper fix, requires data)

**Recommendation**: Use option 1 for immediate deployment, plan option 2 for next model iteration.

---

### Risk 2: Missing Secondary Scores in v2 Cache

**Impact**: Models expecting `personal_attributes_insight` get imputed median (3.0) instead of real scores

**Mitigation**: Complete TASK 1 before using v2 scores in production

**Status**: TASK 1 adds secondary scoring to v2

---

### Risk 3: Dimension Name Mismatches

**Impact**: Code expecting v1 names fails to find v2 dimensions → features default to 0

**Mitigation**: TASK 2 (backward compatibility mapping) prevents this

**Status**: ✅ Complete

---

## Testing Checklist

Before deploying Phase 2 to production:

- [ ] **TASK 1**: Run `python -m pipeline.run_rubric_scoring_v2 -n 10`, verify 21 dimensions per applicant
- [ ] **TASK 1**: Check all secondary scores are 1-4 (not 0 if text exists)
- [ ] **TASK 2**: Load v2 scores with `FeaturePipeline`, verify all `RUBRIC_FEATURES_FINAL` columns present
- [ ] **TASK 3**: Import `config.py` without errors, verify `ALL_RUBRIC_DIMS_V2` includes secondary
- [ ] **TASK 4**: Run `score_pipeline.py` with v2 scores, verify predictions match expected tiers
- [ ] **Integration**: Score 10 applicants end-to-end, validate output with `validate_scores.py`
- [ ] **Validation**: Check parse failure rate < 10%, score distribution (no level > 40%)

---

## Rollback Plan

If Phase 2 breaks production:

1. **Revert to v1 scores**:
   ```bash
   cp data/cache/rubric_scores.json data/cache/rubric_scores_active.json
   ```

2. **Use v1 runner** (deprecated but functional):
   ```bash
   python -m pipeline.run_rubric_scoring_v1_deprecated
   ```

3. **Check feature_engineering.py** auto-detection:
   ```python
   # Should detect v1 format automatically
   pipe = FeaturePipeline(rubric_path='data/cache/rubric_scores.json')
   ```

---

## Files Modified in Phase 2

- ✅ `pipeline/config.py` — Add V2_TO_V1_DIMENSION_MAP (backward compat)
- ✅ `pipeline/feature_engineering.py` — Auto-detect v1/v2, map dimensions
- ⏳ `pipeline/config.py` — Add SECONDARY_DIMS_V2, deprecation comments
- ⏳ `pipeline/rubric_prompts_v2.py` — Add SECONDARY_DIMENSIONS, SECONDARY_PROMPTS
- ⏳ `pipeline/rubric_scorer_v2.py` — Add score_all_secondary_essays()
- ⏳ `pipeline/score_pipeline.py` — Add feature order validation

---

## Next Steps

1. Review this plan with stakeholders
2. Execute TASK 1 (secondary essay scoring)
3. Test with 10 applicants: `python -m pipeline.run_rubric_scoring_v2 -n 10`
4. Validate output: `python -m pipeline.validate_scores data/cache/rubric_scores_v2.json`
5. Execute TASK 3 (config cleanup)
6. Execute TASK 4 (feature ordering)
7. Full integration test with score_pipeline.py
8. Deploy to production

---

## Questions?

See the [detailed implementation plan](2026-02-13-phase2-implementation-plan-detailed.md) for code-level changes, or the [Phase 1 completion doc](2026-02-13-v1-to-v2-migration-completed.md) for architectural context.
