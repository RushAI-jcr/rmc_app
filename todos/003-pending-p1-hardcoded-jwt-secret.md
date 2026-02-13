---
status: pending
priority: p1
issue_id: "003"
tags: [code-review, security, authentication]
---

# Hardcoded JWT Secret with Weak Default

## Problem Statement
`api/settings.py` line 18 has `jwt_secret: str = "dev-secret-key-change-in-production"`. If `.env` is missing `JWT_SECRET`, all JWTs are signed with this publicly-visible string.

## Findings
- **Location**: `api/settings.py` line 18
- **Agent**: security-sentinel, kieran-python-reviewer

## Proposed Solutions
1. Remove default value entirely — force explicit configuration
2. Add startup validation that raises if secret is weak or default in non-dev environments

## Acceptance Criteria
- [ ] No default JWT secret value in code
- [ ] Application fails to start without JWT_SECRET env var (or in non-dev mode with default)
