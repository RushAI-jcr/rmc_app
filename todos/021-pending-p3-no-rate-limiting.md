---
status: pending
priority: P3
issue_id: 021
tags: [security, api, hardening]
---

# Missing Rate Limiting and Security Headers

## Problem Statement

No rate limiting on `/api/auth/login`, no security headers (CSP, X-Frame-Options, HSTS), and overly permissive CORS (`allow_methods=["*"]`).

## Findings

- `api/routers/auth.py`: login endpoint has no rate limiting
- `api/main.py`: CORS middleware uses `allow_methods=["*"]` instead of explicit methods
- No security headers middleware configured (CSP, X-Frame-Options, HSTS)

## Proposed Solutions

- Add `slowapi` rate limiter to the login endpoint (e.g., 5 requests/minute)
- Add security headers middleware (or use `starlette-security-headers`)
- Restrict CORS `allow_methods` to only the HTTP methods actually used (GET, POST, PUT, DELETE)
