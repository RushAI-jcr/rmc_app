---
status: pending
priority: P1
issue_id: 026
tags: [code-review, security, compliance]
dependencies: []
---

# FERPA Audit Logging Incomplete for Read Access

## Problem Statement
FERPA (and institutional policy) requires logging every access to student education records. The plan only mandates audit logging for decision changes (Phase 2). No audit logging exists for: read access to applicant data (GET /api/applicants, GET /api/applicants/{id}), read access to the review queue, read access to fairness reports or SHAP data, or export/bulk-retrieval actions. The current `audit_service.py` only logs: login, logout, upload, preview, approve, retry, pipeline_complete, pipeline_failed.

## Findings
Security sentinel rated this CRITICAL (OWASP A09:2021). The existing `audit_log` table schema already supports this — has `resource_type`, `resource_id`, and `metadata` JSONB fields. No schema changes needed.

## Proposed Solutions
### Option A: Add log_action() calls to all PII-returning endpoints (Recommended)
Add `log_action()` calls to every endpoint that returns applicant PII. At minimum: GET /api/applicants, GET /api/applicants/{id}, GET /api/review/queue, GET /api/review/queue/{amcas_id}/detail, POST /api/review/{amcas_id}/decision, GET /api/fairness/report.
- Pros: Uses existing audit infrastructure, no schema changes needed
- Cons: Requires touching multiple router files
- Effort: Medium (add calls to ~8 endpoints)

## Technical Details
- Affected files: `api/routers/applicants.py`, `api/routers/review.py`, `api/routers/fairness.py`, `api/services/audit_service.py`
- Components: Audit logging, all applicant-data endpoints

## Acceptance Criteria
- [ ] Every endpoint returning applicant PII writes an audit_log entry
- [ ] Audit entries include user_id, resource_type, resource_id, and relevant metadata
- [ ] Audit trail queryable: "who accessed applicant X's data?"

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
