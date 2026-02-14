---
status: pending
priority: P2
issue_id: 030
tags: [code-review, security]
dependencies: []
---

# No Rate Limit on Decision Endpoint

## Problem Statement
No rate limiting on `POST /api/review/{amcas_id}/decision`. A compromised staff account could submit thousands of "confirm" decisions in seconds, rubber-stamping the entire queue. No validation that the amcas_id is actually in the Tier 2+3 review queue. Decisions recorded with valid reviewer_id makes the attack hard to detect.

## Findings
Security sentinel Finding 2 (HIGH, OWASP A04:2021). Maximum ~20 decisions per minute per user recommended (human review speed limit).

## Proposed Solutions
### Option A: Rate limit and validate queue membership
Add rate limiting (~20/min per user) to decision endpoint. Validate amcas_id exists in Tier 2+3 queue before accepting.
- Effort: Small

## Technical Details
- Affected files:
  - api/routers/review.py

## Acceptance Criteria
- [ ] Decision endpoint rate-limited per user
- [ ] amcas_id validated against active review queue

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
