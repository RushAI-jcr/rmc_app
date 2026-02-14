---
status: pending
priority: P3
issue_id: 038
tags: [code-review, performance, database]
dependencies: []
---

# Add Composite Index on (cycle_year, decision)

## Problem Statement
The progress endpoint (`SELECT decision, COUNT(*) FROM review_decisions WHERE cycle_year = ? GROUP BY decision`) and flag summary endpoint need filtered aggregation. Missing composite index on (cycle_year, decision). At 5K rows per cycle, PostgreSQL handles this fine, but the index becomes important with multi-year data accumulation (20K+ rows).

## Findings
Performance oracle Priority 5. Also recommended a partial index for flag summary: `(cycle_year, flag_reason) WHERE decision = 'flag'`.

## Proposed Solutions
### Option A: Add composite and partial indexes in Alembic migration
- Add `ix_review_decisions_cycle_decision` on (cycle_year, decision) and partial index `ix_review_decisions_flags` on (cycle_year, flag_reason) WHERE decision = 'flag'. Include in the Alembic migration.
- Effort: Small (2 lines in migration)

## Technical Details
- Affected files: api/db/models.py (ReviewDecision __table_args__)

## Acceptance Criteria
- [ ] Composite indexes present in Alembic migration
- [ ] Progress and flag summary queries use index scans

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
