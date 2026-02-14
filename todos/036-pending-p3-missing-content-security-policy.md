---
status: pending
priority: P3
issue_id: 036
tags: [code-review, security]
dependencies: []
---

# Missing Content-Security-Policy Header

## Problem Statement
Security headers middleware at `api/main.py` lines 60-67 includes X-Content-Type-Options, X-Frame-Options, HSTS, Referrer-Policy but is missing Content-Security-Policy. Without CSP, a successful XSS attack has no secondary defense.

## Findings
Security sentinel Finding 8 (MEDIUM, OWASP A05:2021). The httpOnly cookie flag prevents direct JS access to JWT (good), but CSP provides defense-in-depth.

## Proposed Solutions
### Option A: Add CSP header to security middleware
- Add CSP header: `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'`
- Effort: Small (1 line)

## Technical Details
- Affected files: api/main.py (security headers middleware)

## Acceptance Criteria
- [ ] Content-Security-Policy header present on all responses
- [ ] Next.js app continues to function correctly with CSP

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
