---
status: pending
priority: p1
issue_id: "001"
tags: [code-review, broken-import, api]
---

# Broken V1 Imports in api/config.py — API Cannot Start

## Problem Statement
`api/config.py` imports 5 symbols removed during v1→v2 migration: `ALL_RUBRIC_DIMS_V1`, `PS_DIMS_V1`, `EXPERIENCE_QUALITY_DIMS_V1`, `SECONDARY_DIMS_V1`, `RUBRIC_FEATURES_FINAL`. These no longer exist in `pipeline/config.py`. The API crashes with `ImportError` at startup. Cascading failure in `api/services/prediction_service.py` (imports `ALL_RUBRIC_DIMS_V1` from `api/config.py`).

## Findings
- **Location**: `api/config.py` lines 29-33, `api/services/prediction_service.py` line 16
- **Agents**: kieran-python-reviewer, code-simplicity-reviewer, architecture-strategist
- **Evidence**: `pipeline/config.py` now exports `ALL_RUBRIC_DIMS`, `PS_DIMS`, `EXPERIENCE_QUALITY_DIMS`, `SECONDARY_DIMS` (no `_V1` suffix, no `RUBRIC_FEATURES_FINAL`)

## Proposed Solutions
1. Update `api/config.py` to import v2 names from `pipeline/config.py`
2. Update `api/services/prediction_service.py` to use v2 names
3. Update `api/routers/applicants.py` RUBRIC_GROUPS to use v2 dimension keys

## Acceptance Criteria
- [ ] `api/config.py` imports successfully
- [ ] `python -c "from api.config import *"` works without error
- [ ] API starts without ImportError
