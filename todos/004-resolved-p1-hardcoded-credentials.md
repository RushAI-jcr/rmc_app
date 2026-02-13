---
status: resolved
priority: p1
issue_id: "004"
tags: [code-review, security, credentials]
---

# Hardcoded Database and Seed Credentials in Version Control

## Problem Statement
Database credentials (`postgres:postgres`) are committed in `alembic.ini` line 4 and `settings.py` line 8. Seed script has `admin/admin` and `staff/staff` passwords.

## Findings
- **Locations**: `api/alembic.ini` line 4, `api/settings.py` line 8, `api/scripts/seed_users.py` lines 17-18
- **Agent**: security-sentinel

## Proposed Solutions
1. Remove hardcoded URL from `alembic.ini` (load from env via `alembic/env.py`)
2. Remove default DB URL from `settings.py`
3. Guard seed script against non-dev environments
4. Create `.env.example` with placeholder values

## Acceptance Criteria
- [ ] No credentials hardcoded in committed files
- [ ] Seed script refuses to run outside development
- [ ] `.env.example` documents required variables
