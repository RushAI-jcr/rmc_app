---
status: complete
priority: p2
issue_id: "012"
tags: [code-review, stale-config, rubric, v1-migration]
completed_at: 2026-02-13
---

# Stale V1 Rubric Groups in Applicants Router

## Problem Statement
`RUBRIC_GROUPS` in the applicants router references v1 dimension keys (e.g., `volunteering_depth`, `shadowing_hours`, etc.) that no longer match the v2 keys exported by `pipeline/config.py`. The scorecard UI shows all zeros because the keys do not match any columns in the scored data.

## Findings
- **Location**: `api/routers/applicants.py` lines 24-68
- **Agent**: code-simplicity-reviewer
- **Evidence**: The hardcoded `RUBRIC_GROUPS` dictionary uses v1 dimension names that were renamed or restructured in the v2 migration. The v2 dimension names live in `pipeline/config.py` and no longer carry the `_V1` suffix or use the old naming convention.

## Resolution
Updated `RUBRIC_GROUPS` to use v2 dimension names from `pipeline/config.py`:
- Imported `PS_DIMS`, `EXPERIENCE_QUALITY_DIMS`, `SECONDARY_DIMS` from `api.config`
- Created `_build_rubric_groups()` function to build groups dynamically from v2 constants
- Organized dimensions into three groups: "Personal Statement", "Experience Quality", and "Secondary Essays"
- All dimension keys now match the v2 rubric scoring output

## Acceptance Criteria
- [x] `RUBRIC_GROUPS` uses v2 dimension names from `pipeline/config.py`
- [x] Scorecard endpoint returns non-zero values for scored applicants
- [x] No hardcoded dimension names remain in the router
- [x] Changes are validated against the current scored dataset
