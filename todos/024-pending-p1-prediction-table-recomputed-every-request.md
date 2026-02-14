---
status: pending
priority: P1
issue_id: 024
tags: [code-review, performance]
dependencies: []
---

# Prediction Table Recomputed on Every Request

## Problem Statement
`build_prediction_table()` in `api/services/prediction_service.py` is called on every API request that touches applicant data (6 call sites: review queue, applicant list, applicant detail, triage summary, triage run, stats overview). Each call copies the entire master DataFrame, merges rubric features, runs scaler.transform(), runs model.predict() and predict_proba(), and builds a list of dicts. At 17K applicants, this is ~50-150ms per request. With 2-5 concurrent reviewers, this wastes ~750ms of CPU per second on identical, redundant computation — the data and models don't change between requests.

## Findings
Performance oracle rated this CRITICAL. Call sites: `review_service.py:28`, `applicants.py:96`, `applicants.py:128`, `triage_service.py:14`, `triage_service.py:31`, `stats.py:18`.

## Proposed Solutions
### Option A: Cache prediction table in DataStore (Recommended)
Cache prediction table in DataStore at startup or first access. Add `_prediction_cache: dict[str, list[dict]]` to DataStore. Invalidate on pipeline run completion. Reduces queue endpoint from ~150ms to <10ms.
- Pros: Clean invalidation, integrates with existing data lifecycle
- Cons: Slightly more code than decorator approach
- Effort: Small (~20 lines)

### Option B: LRU cache with TTL
Add a `@lru_cache` decorator with a TTL. Less clean but faster to implement.
- Pros: Minimal code change
- Cons: TTL-based invalidation may serve stale data briefly
- Effort: Small

## Technical Details
- Affected files: `api/services/data_service.py` (add cache), `api/services/prediction_service.py` (use cache)
- Components: Prediction pipeline, data store, all applicant-facing endpoints

## Acceptance Criteria
- [ ] Queue endpoint responds in <50ms at 17K scale
- [ ] Cache invalidated after pipeline run completes
- [ ] No stale data served after new data is loaded

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
