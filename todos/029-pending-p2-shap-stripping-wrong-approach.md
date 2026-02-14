---
status: pending
priority: P2
issue_id: 029
tags: [code-review, security, python]
dependencies: []
---

# SHAP Stripping Is Wrong Approach — Use Separate Response Models

## Problem Statement
Plan proposes stripping SHAP data by returning empty arrays (`shap_drivers: []`, `class_probabilities: []`) for staff users. This is misleading — a consumer can't distinguish "no data" from "not authorized." Multiple data leak vectors also exist: stats endpoint returns bakeoff/models_loaded, triage summary returns tier distributions.

## Findings
Python reviewer and security sentinel (Finding 5) both flagged this. Security sentinel identified 4 additional leak vectors beyond SHAP.

## Proposed Solutions
### Option A: Separate Pydantic response models (Recommended)
Use separate Pydantic response models — `ApplicantDetail` for staff, `ApplicantDetailAdmin(ApplicantDetail)` for admin. Schema-level guarantee, not runtime mutation.
- Effort: Medium

### Option B: Admin-only SHAP endpoint
Create `GET /api/applicants/{id}/shap` as admin-only endpoint. Base endpoint never returns SHAP.
- Effort: Medium

## Technical Details
- Affected files:
  - api/routers/applicants.py
  - api/models/review.py (Pydantic models)

## Acceptance Criteria
- [ ] Staff response model physically cannot contain SHAP fields
- [ ] Stats/triage endpoints restricted to admin or return reduced payload for staff

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
