---
status: pending
priority: P2
issue_id: 031
tags: [code-review, security, infrastructure]
dependencies: []
---

# In-Memory Rate Limiter Breaks Under Multiple Replicas

## Problem Statement
Login rate limiter at `api/routers/auth.py` lines 21-23 uses in-memory `defaultdict`. Azure Container Apps runs multiple replicas, so attacker gets 5 * N attempts. Also uses `request.client.host` which behind a load balancer/proxy is the proxy's IP, not the client's — all users share the same rate limit bucket.

## Findings
Security sentinel Finding 3 (HIGH). Redis is already in the stack per `settings.redis_url`.

## Proposed Solutions
### Option A: Move rate limiter to Redis
Move rate limiter to Redis (sliding window counter keyed on client IP). Read client IP from `X-Forwarded-For` with proper validation.
- Effort: Medium

## Technical Details
- Affected files:
  - api/routers/auth.py (lines 21-30)

## Acceptance Criteria
- [ ] Rate limiting works across multiple replicas
- [ ] Client IP correctly identified behind reverse proxy

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
