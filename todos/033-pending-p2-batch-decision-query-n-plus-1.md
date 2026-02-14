---
status: pending
priority: P2
issue_id: 033
tags: [code-review, performance]
dependencies: []
---

# Batch Decision Query to Avoid N+1 in Review Queue

## Problem Statement
After Phase 2 migration, the review queue endpoint must merge in-memory predictions with PostgreSQL decisions. If decisions are queried per-applicant (N+1), that's 4-5K individual SELECT queries (~4-5 seconds). Must use a single batch query and in-memory merge. Also, concurrent reviewer awareness (reviewer usernames) needs joinedload to avoid another N+1 on the users table.

## Findings
Performance oracle identified 3 N+1 risks. Architecture strategist confirmed the hybrid join must be application-level, not SQL.

## Proposed Solutions
### Option A: Single batch query with joinedload
Single `SELECT * FROM review_decisions WHERE cycle_year = ?` with `joinedload(ReviewDecision.reviewer)`. Merge with predictions in Python dict. O(n + m).
- Effort: Small (implementation detail in Phase 2)

## Technical Details
- Affected files:
  - api/services/review_service.py (get_review_queue)

## Acceptance Criteria
- [ ] Queue endpoint makes exactly 1 DB query for decisions
- [ ] No per-applicant DB lookups
- [ ] Reviewer usernames loaded without additional queries

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
