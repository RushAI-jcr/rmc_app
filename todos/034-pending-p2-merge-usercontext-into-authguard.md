---
status: pending
priority: P2
issue_id: 034
tags: [code-review, architecture, frontend]
dependencies: []
---

# Merge UserContext Into AuthGuard to Avoid Duplicate API Calls

## Problem Statement
Plan proposes a new UserContext provider in `frontend/contexts/user-context.tsx` that wraps the layout. But AuthGuard at `frontend/components/auth-guard.tsx` already calls `getMe()` on every navigation and discards the result (line 23). Adding a separate UserProvider would cause two identical API calls per page navigation.

## Findings
Architecture strategist identified this. AuthGuard already has the getMe() call — it should store the response in context and expose it to children.

## Proposed Solutions
### Option A: Merge UserContext into AuthGuard (Recommended)
AuthGuard stores getMe() result in React context, exports useUser() hook. One component, one API call.
- Effort: Small

## Technical Details
- Affected files:
  - frontend/components/auth-guard.tsx
  - frontend/components/ui/sidebar.tsx

## Acceptance Criteria
- [ ] Single getMe() call per navigation
- [ ] useUser() hook available to all children
- [ ] No separate UserProvider wrapper

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
