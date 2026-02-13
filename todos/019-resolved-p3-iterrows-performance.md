---
status: resolved
priority: P3
issue_id: 019
tags: [performance, pandas]
---

# `.iterrows()` Performance in Data Preparation

## Problem Statement

`build_personal_statements_dict()` and `build_secondary_texts_dict()` use `.iterrows()`, which is ~100x slower than vectorized approaches.

## Findings

- `pipeline/data_preparation.py` line 577: `build_personal_statements_dict()` uses `.iterrows()`
- `pipeline/data_preparation.py` line 608: `build_secondary_texts_dict()` uses `.iterrows()`

## Proposed Solutions

- Replace with `dict(zip(df[key_col], df[value_col]))` after vectorized filtering
- For more complex row logic, use `.apply()` or `.to_dict(orient='records')`
