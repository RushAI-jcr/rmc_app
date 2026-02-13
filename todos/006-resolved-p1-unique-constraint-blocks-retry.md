---
status: resolved
priority: p1
issue_id: "006"
tags: [code-review, database, constraint]
---

# UniqueConstraint on PipelineRun Blocks Retry Flow

## Problem Statement
ORM model declares `UniqueConstraint("upload_session_id")` which prevents ANY second PipelineRun per session. The Alembic migration correctly uses a partial unique index (only active runs). The retry endpoint creates a new PipelineRun for the same session, which will fail with IntegrityError if ORM creates the tables.

## Findings
- **Location**: `api/db/models.py` lines 104-108 vs migration lines 84-88
- **Agents**: kieran-python-reviewer, architecture-strategist

## Proposed Solutions
Replace the UniqueConstraint with a partial Index matching the migration:
```python
Index(
    "uq_pipeline_runs_active",
    "upload_session_id",
    unique=True,
    postgresql_where=text("status IN ('pending', 'running')"),
)
```

## Acceptance Criteria
- [ ] ORM model and migration produce identical constraints
- [ ] Retry endpoint can create a new PipelineRun for a completed session
