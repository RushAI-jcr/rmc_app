---
status: pending
priority: p2
issue_id: "007"
tags: [code-review, security, idor, authorization]
---

# Missing IDOR Protection on Ingest Endpoints

## Problem Statement
All ingest endpoints accept `session_id` without filtering by the current user. Any authenticated user can access or modify ANY upload session by guessing or enumerating session IDs. This is a classic Insecure Direct Object Reference (IDOR) vulnerability.

## Findings
- **Location**: `api/routers/ingest.py` lines 94-279
- **Agent**: security-sentinel
- **Evidence**: Endpoints retrieve sessions by `session_id` alone with no ownership check. Any authenticated user can view, modify, or delete another user's upload session.

## Proposed Solutions
Add an ownership check after retrieving the session:
```python
session = get_session(session_id)
if session.uploaded_by != user.id and not user.is_admin:
    raise HTTPException(status_code=403, detail="Not authorized to access this session")
```
Apply this pattern to every endpoint that accepts a `session_id` parameter.

## Acceptance Criteria
- [ ] Every ingest endpoint verifies `session.uploaded_by == user.id` before proceeding
- [ ] Admin role can override the ownership check
- [ ] Unauthorized access returns 403 Forbidden
- [ ] Unit tests confirm cross-user access is blocked
