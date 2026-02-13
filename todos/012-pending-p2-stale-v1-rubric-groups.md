---
status: pending
priority: p2
issue_id: "012"
tags: [code-review, stale-config, rubric, v1-migration]
---

# Stale V1 Rubric Groups in Applicants Router

## Problem Statement
`RUBRIC_GROUPS` in the applicants router references v1 dimension keys (e.g., `volunteering_depth`, `shadowing_hours`, etc.) that no longer match the v2 keys exported by `pipeline/config.py`. The scorecard UI shows all zeros because the keys do not match any columns in the scored data.

## Findings
- **Location**: `api/routers/applicants.py` lines 24-68
- **Agent**: code-simplicity-reviewer
- **Evidence**: The hardcoded `RUBRIC_GROUPS` dictionary uses v1 dimension names that were renamed or restructured in the v2 migration. The v2 dimension names live in `pipeline/config.py` and no longer carry the `_V1` suffix or use the old naming convention.

## Proposed Solutions
Update `RUBRIC_GROUPS` to use the v2 dimension names from `pipeline/config.py`:
```python
from pipeline.config import ALL_RUBRIC_DIMS, PS_DIMS, EXPERIENCE_QUALITY_DIMS, SECONDARY_DIMS

RUBRIC_GROUPS = {
    "Personal Statement": PS_DIMS,
    "Experience Quality": EXPERIENCE_QUALITY_DIMS,
    "Secondary Factors": SECONDARY_DIMS,
}
```
This ensures the groups always stay in sync with the pipeline config.

## Acceptance Criteria
- [ ] `RUBRIC_GROUPS` uses v2 dimension names from `pipeline/config.py`
- [ ] Scorecard endpoint returns non-zero values for scored applicants
- [ ] No hardcoded dimension names remain in the router
- [ ] Changes are validated against the current scored dataset
