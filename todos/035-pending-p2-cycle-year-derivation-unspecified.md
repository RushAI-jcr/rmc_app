---
status: pending
priority: P2
issue_id: 035
tags: [code-review, architecture]
dependencies: []
---

# cycle_year Derivation Unspecified in Plan

## Problem Statement
Plan says `cycle_year` is `Integer, nullable=False` on ReviewDecision and passed to save_decision(), but never specifies where the value comes from. The frontend has no way to determine the current cycle year. The existing review router doesn't pass cycle_year to submit_decision. The migration script also needs to know what cycle_year to assign to pre-existing JSON decisions (which have no cycle year).

## Findings
Python reviewer and architecture strategist both flagged this gap. Options: derive from active UploadSession, pass from frontend, or return from a config endpoint.

## Proposed Solutions
### Option A: Derive from active UploadSession
Derive from the active UploadSession (the one with `is_active=True`). Add cycle_year to the review queue response or to GET /api/auth/me.
- Effort: Small

## Technical Details
- Affected files:
  - api/routers/review.py
  - api/services/review_service.py
  - plan document

## Acceptance Criteria
- [ ] cycle_year derivation documented
- [ ] Frontend can determine current cycle year
- [ ] Migration script has documented defaults for pre-existing data

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
