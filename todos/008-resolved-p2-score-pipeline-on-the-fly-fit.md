---
status: resolved
priority: p2
issue_id: "008"
tags: [code-review, data-leakage, pipeline, scoring]
---

# Score Pipeline Fallback Fits FeaturePipeline on Scoring Data

## Problem Statement
`score_pipeline.py` lines 102-108 contain a fallback that fits the `FeaturePipeline` on scoring data when no saved pipeline exists. This breaks the leakage-prevention contract by allowing the feature pipeline to learn statistics (means, scales, encodings) from the data being scored rather than from the training data.

## Findings
- **Location**: `pipeline/score_pipeline.py` lines 102-108
- **Agent**: architecture-strategist
- **Evidence**: The fallback path calls `pipeline.fit(scoring_data)` instead of failing fast when no pre-fitted pipeline artifact is found. This silently introduces data leakage, producing scores that are not comparable to training-time scores.

## Proposed Solutions
Remove the fallback entirely and raise an error if the saved pipeline does not exist:
```python
pipeline_path = get_pipeline_path()
if not pipeline_path.exists():
    raise FileNotFoundError(
        f"No fitted pipeline found at {pipeline_path}. "
        "Run the training pipeline first to generate the artifact."
    )
pipeline = load_pipeline(pipeline_path)
```

## Acceptance Criteria
- [ ] Fallback `fit()` on scoring data is removed
- [ ] `FileNotFoundError` is raised when no saved pipeline exists
- [ ] Error message clearly instructs the user to run training first
- [ ] Existing tests updated to reflect the new behavior
