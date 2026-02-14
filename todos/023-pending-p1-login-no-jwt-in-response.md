---
status: pending
priority: P1
issue_id: 023
tags: [code-review, security, agent-native]
dependencies: []
---

# Login Endpoint Does Not Return JWT in Response Body

## Problem Statement
The login endpoint at `api/routers/auth.py` line 74 returns `{"status": "ok", "username": "..."}` with the JWT only in an httpOnly cookie. The `get_current_user` dependency at `api/dependencies.py` lines 16-18 supports Bearer tokens, but no client can ever obtain one — the login never returns the token in the response body. AI agents and programmatic clients cannot authenticate.

## Findings
Agent-native reviewer identified this as the single critical blocker for agent parity. Score: 14/16 capabilities agent-accessible, but this blocks ALL of them.

## Proposed Solutions
### Option A: Return token in login response (Recommended)
Add `"access_token": token, "token_type": "bearer"` to the login response dict at `api/routers/auth.py` line 74. Single-line change. Cookie continues to work for browsers.
- Pros: Minimal change, enables all programmatic clients immediately
- Cons: Token now visible in response body (acceptable for authenticated endpoint)
- Effort: Small (1 line)

### Option B: Create a separate token endpoint
Create a separate `POST /api/auth/token` endpoint for programmatic clients.
- Pros: Clean separation of browser vs programmatic auth
- Cons: Adds API surface area unnecessarily
- Effort: Small but adds surface area

## Technical Details
- Affected files: `api/routers/auth.py` (line 74)
- Components: Authentication, login endpoint

## Acceptance Criteria
- [ ] Login response includes `access_token` and `token_type` fields
- [ ] Bearer token obtained from login works with `GET /api/review/queue`

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
