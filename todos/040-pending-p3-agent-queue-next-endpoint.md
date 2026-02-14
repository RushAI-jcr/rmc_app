---
status: pending
priority: P3
issue_id: 040
tags: [code-review, agent-native]
dependencies: []
---

# Add GET /api/review/queue/next Endpoint

## Problem Statement
No API primitive for "next unreviewed applicant." An agent reviewing 4K+ applicants must fetch the entire queue each iteration to find the next item. The frontend maintains `currentIdx` in React state (UI-only), with no server-side equivalent.

## Findings
Agent-native reviewer (Warning 4). Proposed `GET /api/review/queue/next` returning single next-unreviewed applicant with same priority sorting. Enables efficient agent loop: `while item = GET next: review(item); submit(item)`.

## Proposed Solutions
### Option A: Add queue/next endpoint
- Add `GET /api/review/queue/next` endpoint. Returns first item from queue where decision IS NULL. Returns 204 No Content when queue is complete.
- Effort: Small (~10 lines)

## Technical Details
- Affected files: api/routers/review.py, api/services/review_service.py

## Acceptance Criteria
- [ ] Endpoint returns single next-unreviewed applicant
- [ ] Returns 204 when all applicants reviewed
- [ ] Uses same priority sorting as full queue

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
