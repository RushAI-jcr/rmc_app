---
status: resolved
priority: p2
issue_id: "013"
tags: [code-review, celery, reliability, timeout]
---

# No Time Limit on Celery Pipeline Task

## Problem Statement
The Celery pipeline task has no `time_limit` or `soft_time_limit` configured. A worker can hang indefinitely when processing corrupt files, encountering infinite loops, or loading unexpectedly large models, consuming the worker slot forever.

## Findings
- **Location**: `api/tasks/pipeline_task.py` line 17
- **Agent**: performance-oracle
- **Evidence**: The `@celery_app.task` decorator has no timeout parameters. In production, a single hung task can exhaust the worker pool if enough accumulate, leading to a full pipeline outage.

## Proposed Solutions
Add time limits to the task decorator:
```python
@celery_app.task(
    bind=True,
    soft_time_limit=300,   # 5 minutes — raises SoftTimeLimitExceeded
    time_limit=360,        # 6 minutes — hard kill
)
def run_pipeline_task(self, session_id: str, ...):
    try:
        ...
    except SoftTimeLimitExceeded:
        update_session_status(session_id, "failed", error="Pipeline timed out after 5 minutes")
        raise
```

## Acceptance Criteria
- [ ] `soft_time_limit=300` is set on the pipeline task
- [ ] `time_limit=360` is set as a hard kill fallback
- [ ] `SoftTimeLimitExceeded` is caught and session status is updated to "failed"
- [ ] Timeout values are configurable via environment variables or settings
