---
status: pending
priority: P3
issue_id: 037
tags: [code-review, python, database]
dependencies: []
---

# Tier and Score Snapshot Columns on ReviewDecision

## Problem Statement
When a decision is made, the model's prediction at that moment is meaningful. If the model is retrained and scores change, the historical context of why a reviewer confirmed or flagged is lost. The plan's ReviewDecision model has no record of what the AI predicted at decision time.

## Findings
Python reviewer recommended `tier_at_decision: int` and `predicted_score_at_decision: float` columns. Important for annual retrain analysis and audit trail.

## Proposed Solutions
### Option A: Add snapshot columns to ReviewDecision
- Add `tier_at_decision` (Integer) and `predicted_score_at_decision` (Float) columns to ReviewDecision. Populate from prediction data at save time.
- Effort: Small (2 columns + populate at save)

## Technical Details
- Affected files: api/db/models.py (ReviewDecision), api/services/review_service.py (save_decision)

## Acceptance Criteria
- [ ] Decision records include the AI prediction at the time of review
- [ ] Columns populated automatically on every decision save

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
