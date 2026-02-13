---
status: complete
priority: p2
issue_id: "014"
tags: [code-review, ux, progress-reporting, pipeline]
completed_at: 2026-02-13
---

# Non-Monotonic Progress Reporting in Score Pipeline

## Problem Statement
`score_pipeline.py` passes the progress callback to `prepare_dataset()`, which reports its own progress values (0, 10, 20, 30, 40). Then `score_pipeline` itself reports 10, 40, 80, 100. The progress bar jumps backward (e.g., 40 -> 10) from the user's perspective, creating a confusing and broken UX.

## Findings
- **Location**: `pipeline/score_pipeline.py` lines 73-83
- **Agent**: architecture-strategist
- **Evidence**: Both `prepare_dataset()` and the calling function emit progress values on the same callback without coordination. The resulting sequence seen by the client is non-monotonic: `0, 10, 20, 30, 40, 10, 40, 80, 100`.

## Resolution
Implemented Option A: Report progress only from the top-level orchestrator. Changes made:
- Removed intermediate progress callbacks between major steps
- Ensured `prepare_dataset()` is called without a nested progress callback
- Updated progress sequence to: 0 (ingestion start), 10 (ingestion complete), 40 (features complete), 70 (ml_scoring complete), 100 (triage complete)
- Updated docstring to reflect the new progress ranges

The progress values are now strictly monotonically increasing with no backward jumps.

## Acceptance Criteria
- [x] Progress values reported to the client are strictly monotonically increasing
- [x] No backward jumps occur during any pipeline execution path
- [x] Sub-task progress is either suppressed or mapped to a sub-range
- [x] End-to-end test verifies monotonicity of progress sequence
