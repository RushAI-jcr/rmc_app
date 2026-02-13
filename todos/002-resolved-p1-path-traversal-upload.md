---
status: resolved
priority: p1
issue_id: "002"
tags: [code-review, security, path-traversal]
---

# Path Traversal in File Upload

## Problem Statement
`upload_service.py` line 89 uses `session_dir / f.filename` without sanitizing the filename. An attacker can upload `../../etc/cron.d/malicious` to write files outside the session directory.

## Findings
- **Location**: `api/services/upload_service.py` line 89
- **Agent**: security-sentinel
- **Severity**: CRITICAL — allows arbitrary file writes

## Proposed Solutions
```python
from pathlib import PurePosixPath
safe_name = PurePosixPath(f.filename).name
if not safe_name or safe_name.startswith('.'):
    errors.append(f"Invalid filename: {f.filename}")
    continue
dest = session_dir / safe_name
if not dest.resolve().is_relative_to(session_dir.resolve()):
    errors.append(f"Path traversal attempt: {f.filename}")
    continue
```

## Acceptance Criteria
- [ ] Filenames are sanitized (directory components stripped)
- [ ] Resolved path is verified to be under session_dir
- [ ] Dotfiles are rejected
