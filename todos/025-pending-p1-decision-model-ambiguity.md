---
status: pending
priority: P1
issue_id: 025
tags: [code-review, architecture, database]
dependencies: []
---

# Decision Model Cardinality Ambiguity

## Problem Statement
The plan proposes a unique constraint on `(reviewer_id, amcas_id, cycle_year)` — one decision per reviewer per applicant per cycle. But the current system uses `store.decisions[amcas_id]` — one decision per applicant, period. The plan also says "last write wins" and shows queue items with a single `decision` field. These semantics are contradictory: if two reviewers can have different decisions for the same applicant, which is canonical? If Reviewer A confirms and Reviewer B flags, what is the applicant's status?

## Findings
Identified by architecture-strategist, python-reviewer, performance-oracle, and security-sentinel (Finding 7). All four agents flagged this as unresolved. The security reviewer noted this is a data integrity risk for medical school admissions.

## Proposed Solutions
### Option A: Single canonical decision per applicant per cycle (Recommended for MVP)
Unique constraint on `(amcas_id, cycle_year)` only — one canonical decision per applicant per cycle. Keep `reviewer_id` as a non-unique column for audit. Matches current single-decision semantics. Simple.
- Pros: Matches existing behavior, no ambiguity, simple to implement
- Cons: Does not support committee-style multi-reviewer workflows
- Effort: Small (schema change only)

### Option B: Per-reviewer decisions with consensus logic
Per-reviewer decisions with consensus/resolution logic. More complex, enables committee review. Not MVP.
- Pros: Supports multi-reviewer workflows
- Cons: Requires consensus resolution logic, UI for conflicts, significantly more complex
- Effort: Large

## Technical Details
- Affected files: Plan document (schema section), `api/db/models.py` (new ReviewDecision model)
- Components: Decision persistence, review queue, data model

## Acceptance Criteria
- [ ] Decision cardinality documented in plan
- [ ] Unique constraint matches documented semantics
- [ ] Queue endpoint returns unambiguous decision status per applicant

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
