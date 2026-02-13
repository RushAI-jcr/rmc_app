---
status: resolved
priority: p2
issue_id: "009"
tags: [code-review, auth, api, agent-access]
---

# Cookie-Only Auth Blocks Programmatic and Agent Access

## Problem Statement
`get_current_user` only reads cookies for authentication and does not support `Authorization: Bearer <token>` headers. This blocks all programmatic clients, CI/CD integrations, and AI agent access from using the API.

## Findings
- **Location**: `api/dependencies.py` line 13
- **Agent**: agent-native-reviewer
- **Evidence**: The dependency function calls `request.cookies.get("session_token")` exclusively. Any client that cannot set cookies (CLI tools, API scripts, agents) is unable to authenticate.

## Proposed Solutions
Add Bearer token extraction as the primary method, with cookie as fallback:
```python
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    token = None
    # 1. Try Bearer header first
    if credentials:
        token = credentials.credentials
    # 2. Fall back to cookie
    if not token:
        token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await validate_token(token)
```

## Acceptance Criteria
- [ ] `Authorization: Bearer <token>` header is accepted for authentication
- [ ] Cookie-based auth continues to work as a fallback
- [ ] Unauthenticated requests return 401 regardless of method
- [ ] OpenAPI docs reflect the Bearer scheme
