---
status: pending
priority: P3
issue_id: 039
tags: [code-review, python, database]
dependencies: []
---

# Use ondelete=RESTRICT for reviewer_id Foreign Key

## Problem Statement
Plan proposes `reviewer_id` with `ondelete="SET NULL"`. When a user is deleted, all their decision attributions are lost. For FERPA-adjacent audit requirements, this is problematic. Should never delete a user who has made review decisions.

## Findings
Python reviewer recommended `ondelete="RESTRICT"`. If user deactivation is needed, add `is_active` column (already recommended in P2 todo 032).

## Proposed Solutions
### Option A: Use ondelete=RESTRICT with is_active flag for deactivation
- Use `ondelete="RESTRICT"`. Prevent deletion of users with existing decisions. Use `is_active` flag for deactivation.
- Effort: Small

## Technical Details
- Affected files: api/db/models.py (ReviewDecision.reviewer_id FK)

## Acceptance Criteria
- [ ] Attempting to delete a user with decisions raises an IntegrityError
- [ ] User deactivation via is_active flag instead of deletion

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
