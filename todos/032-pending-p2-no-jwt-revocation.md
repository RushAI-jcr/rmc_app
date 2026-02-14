---
status: pending
priority: P2
issue_id: 032
tags: [code-review, security]
dependencies: []
---

# No JWT Revocation Mechanism

## Problem Statement
No JWT revocation mechanism. Terminated staff member's 8-hour JWT remains valid until natural expiry. `get_current_user()` checks user exists in DB but there is no `is_active` flag — only way to revoke is delete the user record, which would lose audit attribution.

## Findings
Security sentinel Finding 4 (HIGH, OWASP A07:2021). 8 hours of unauthorized access after credential compromise.

## Proposed Solutions
### Option A: Add is_active flag to User model (Recommended)
Add `is_active` boolean to User model. Check in `get_current_user()`. Deactivating a user immediately invalidates sessions.
- Effort: Small (Alembic migration + 2-line check)

### Option B: Redis-backed JWT blocklist
On logout, add `jti` to blocklist with TTL.
- Effort: Medium

## Technical Details
- Affected files:
  - api/db/models.py (User model)
  - api/dependencies.py (get_current_user)

## Acceptance Criteria
- [ ] Deactivated user cannot access any endpoint
- [ ] Existing audit data preserved when user deactivated

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
