---
status: pending
priority: p2
issue_id: "014"
tags: [code-review, ux, progress-reporting, pipeline]
---

# Non-Monotonic Progress Reporting in Score Pipeline

## Problem Statement
`score_pipeline.py` passes the progress callback to `prepare_dataset()`, which reports its own progress values (0, 10, 20, 30, 40). Then `score_pipeline` itself reports 10, 40, 80, 100. The progress bar jumps backward (e.g., 40 -> 10) from the user's perspective, creating a confusing and broken UX.

## Findings
- **Location**: `pipeline/score_pipeline.py` lines 73-83
- **Agent**: architecture-strategist
- **Evidence**: Both `prepare_dataset()` and the calling function emit progress values on the same callback without coordination. The resulting sequence seen by the client is non-monotonic: `0, 10, 20, 30, 40, 10, 40, 80, 100`.

## Proposed Solutions
Option A: Do not pass the callback to `prepare_dataset()`. Report progress only from the top-level orchestrator:
```python
# score_pipeline.py
callback(5, "Preparing dataset...")
dataset = prepare_dataset(data)  # no callback passed
callback(30, "Running feature engineering...")
```

Option B: Wrap the callback in a range scaler so sub-tasks report within an assigned range:
```python
def scoped_callback(start, end, inner_callback):
    def wrapper(pct, msg=""):
        scaled = start + (pct / 100) * (end - start)
        inner_callback(int(scaled), msg)
    return wrapper

# prepare_dataset gets 0-30% range
dataset = prepare_dataset(data, callback=scoped_callback(0, 30, callback))
# scoring gets 30-100% range
callback(30, "Scoring...")
```

## Acceptance Criteria
- [ ] Progress values reported to the client are strictly monotonically increasing
- [ ] No backward jumps occur during any pipeline execution path
- [ ] Sub-task progress is either suppressed or mapped to a sub-range
- [ ] End-to-end test verifies monotonicity of progress sequence
