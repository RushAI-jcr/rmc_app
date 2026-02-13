---
status: resolved
priority: p2
issue_id: "011"
tags: [code-review, performance, feature-engineering, pipeline]
---

# Double Transform During fit_transform

## Problem Statement
`fit_transform()` calls `fit()` which internally runs `_transform_impl()`, then separately calls `transform()` which runs `_transform_impl()` again. Training data is transformed twice, wasting compute on potentially expensive feature engineering operations.

## Findings
- **Location**: `pipeline/feature_engineering.py` lines 90-153
- **Agents**: performance-oracle, kieran-python-reviewer
- **Evidence**: `fit()` computes transformed output internally (to learn statistics), then `fit_transform()` calls `transform()` which recomputes the same transformation. The intermediate result from `fit()` is discarded.

## Proposed Solutions
Cache the result from `fit()`'s internal transform and reuse it in `fit_transform()`:
```python
def fit(self, df: pd.DataFrame) -> "FeaturePipeline":
    self._fitted_result = self._transform_impl(df, fitting=True)
    return self

def transform(self, df: pd.DataFrame) -> pd.DataFrame:
    return self._transform_impl(df, fitting=False)

def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
    self.fit(df)
    return self._fitted_result
```

## Acceptance Criteria
- [ ] `fit_transform()` calls `_transform_impl()` exactly once
- [ ] `transform()` on new data still works correctly
- [ ] Output of `fit_transform(X)` is identical to `fit(X).transform(X)`
- [ ] `_fitted_result` is cleared or managed to avoid stale state
