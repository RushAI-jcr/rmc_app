---
title: "Score 50 More Applicants + Feature Selection for GO/NO-GO"
type: feat
date: 2026-02-14
---

# Score 50 More Applicants + Feature Selection for GO/NO-GO

## Overview

The 50-record pilot test returned **INCONCLUSIVE** (1/3 criteria passed). Diagnostic analysis revealed the root cause: **21 features on 50 records (p/n=0.41) causes overfitting** — 18 noise dimensions drown out 3 signal dimensions. Feature-selected models (k=2) show R2 flipping from -0.077 to +0.087.

**This plan:** Score 50 more applicants (stratified) on all 21 dims, then feature-select to make a definitive GO/NO-GO decision with n=100 and optimal feature set.

## Problem Statement

| Metric | All 21 dims (n=51) | Top 2 dims (n=51) | Goal (n=100, k=best) |
|--------|--------------------|--------------------|----------------------|
| MAE improvement | +0.03 | +0.37 | Definitive signal |
| R2 | -0.047 | +0.087 | > 0.05 |
| Statistical power | 0.79 | 0.79 | > 0.95 |
| p/n ratio | 0.43 | 0.06 | < 0.15 |

## Proposed Solution

Three sequential steps, each building on the prior:

### Step 1: Stratified Selection of 50 More Applicants (~5 min)

Create `pipeline/select_pilot_batch2.py` that:
1. Loads the 2024 test set (n=613) and existing scored IDs (n=50)
2. Stratifies remaining 563 applicants by tier distribution
3. Selects 50 using proportional stratified sampling matching the full pool:
   - Tier 0 (0-6.25): ~9 applicants (17.0%)
   - Tier 1 (6.25-12.5): ~6 applicants (11.6%)
   - Tier 2 (12.5-18.75): ~10 applicants (20.9%)
   - Tier 3 (18.75-25): ~25 applicants (50.6%)
4. Outputs list of AMCAS IDs to `data/cache/pilot_batch2_ids.json`

### Step 2: Score 50 More Applicants (~25 min, ~$16)

Use the existing scorer:
```bash
python -m pipeline.run_rubric_scoring_v2 --years 2024 --resume
```

But we need to target specific IDs. Two approaches:
- **Option A:** Add `--id-file` flag to `run_rubric_scoring_v2.py` that reads IDs from a JSON file
- **Option B:** Use existing `--amcas-id` flag in a loop script

Option A is cleaner. Add a `--id-file` argument that loads IDs from JSON and filters to only score those applicants.

**Cost:** 50 applicants x 21 calls x $0.015 = **$15.75**
**Time:** 50 x 28s = **~23 minutes**

### Step 3: Enhanced Pilot Test with Feature Selection (~5 sec)

Update `pipeline/pilot_test.py` to add:
1. **Feature selection sweep**: Test k=1,2,3,5,7,10,15,21 and report best k
2. **Auto-select optimal k**: Choose k that maximizes LOO-CV R2 on the stacking model
3. **Revised GO/NO-GO**: Use feature-selected model metrics, not all-21 metrics
4. **Recommended rubric**: Output which specific dimensions to keep

New output section:
```
--- Feature Selection ---
k dims    p/n     MAE     R2      BktAcc  Kappa   MAE_d
PlanA     0.01    X.XX    X.XXX   XX.X%   X.XXX   ---
k=2       0.03    X.XX    X.XXX   XX.X%   X.XXX   +X.XX
k=3*      0.04    X.XX    X.XXX   XX.X%   X.XXX   +X.XX  <-- optimal
...
k=21      0.22    X.XX    X.XXX   XX.X%   X.XXX   +X.XX

* Selected k=3: adversity_resilience, motivation_depth, adversity_response_quality
```

## Acceptance Criteria

- [ ] `select_pilot_batch2.py` selects 50 IDs stratified by tier, saves to JSON
- [ ] `run_rubric_scoring_v2.py` supports `--id-file` flag to score specific applicants
- [ ] All 50 new applicants scored and appended to `rubric_scores_v2.json`
- [ ] `pilot_test.py` includes feature selection sweep (k=1..21)
- [ ] Pilot test runs on n=100 with feature-selected model
- [ ] Report includes clear GO/NO-GO with feature-selected metrics
- [ ] Report recommends specific dims to keep if GO

## Technical Details

### Files Modified
- `pipeline/run_rubric_scoring_v2.py` — add `--id-file` argument
- `pipeline/pilot_test.py` — add feature selection analysis

### Files Created
- `pipeline/select_pilot_batch2.py` — stratified ID selection script (~60 lines)

### Dependencies
- Existing: numpy, pandas, scipy, sklearn, json
- Azure OpenAI API access (for Step 2 scoring)

## Execution Order

```
1. python -m pipeline.select_pilot_batch2                     # Select 50 IDs (~5 sec)
2. python -m pipeline.run_rubric_scoring_v2 \
     --id-file data/cache/pilot_batch2_ids.json --resume      # Score them (~25 min)
3. python -m pipeline.pilot_test                               # Re-analyze n=100 (~5 sec)
```

Total wall time: ~30 minutes (25 min is LLM scoring)
Total cost: ~$16

## References

- Pilot test results: [pilot_report.txt](data/processed/pilot_report.txt)
- Feature count diagnostic (this session): k=2 optimal for continuous, k=7-10 for classification
- Power analysis: n=100 with r=0.377 gives power=0.98
- Existing scorer: [run_rubric_scoring_v2.py](pipeline/run_rubric_scoring_v2.py)
- Existing pilot test: [pilot_test.py](pipeline/pilot_test.py)
