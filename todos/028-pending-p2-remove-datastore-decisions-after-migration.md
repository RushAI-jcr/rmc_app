---
status: pending
priority: P2
issue_id: 028
tags: [code-review, architecture, python]
dependencies: []
---

# Remove DataStore.decisions After PostgreSQL Migration

## Problem Statement
After Phase 2 migrates decisions to PostgreSQL, `DataStore.decisions` (in-memory dict at `api/services/data_service.py` line 33) must be removed. If both exist, there are two sources of truth — guaranteed bug. The plan does not explicitly state removal of `DataStore.decisions`, `load_decisions()`, `_persist_decisions()`, or the startup call in `api/main.py` line 44.

## Findings
Python reviewer and architecture strategist both independently flagged this. All code paths reading `store.decisions` (appears in data_service.py, review_service.py, applicants.py, main.py) must be updated to query PostgreSQL.

## Proposed Solutions
### Option A: Remove DataStore.decisions and migrate all reads to PostgreSQL
After Phase 2, remove DataStore.decisions, load_decisions(), _persist_decisions(), and the startup call. Update all read sites to query PostgreSQL via review_service.
- Effort: Medium

## Technical Details
- Affected files:
  - api/services/data_service.py
  - api/services/review_service.py
  - api/routers/applicants.py
  - api/main.py

## Acceptance Criteria
- [ ] No reference to store.decisions remains in codebase
- [ ] All decision reads come from PostgreSQL
- [ ] load_decisions() removed from startup

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
