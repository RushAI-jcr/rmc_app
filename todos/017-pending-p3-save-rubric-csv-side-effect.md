---
status: pending
priority: P3
issue_id: 017
tags: [side-effect, pipeline, correctness]
---

# `_save_rubric_csv()` Side Effect in Transform Path

## Problem Statement

`_save_rubric_csv()` writes a CSV file on every `transform()` call, including production scoring runs. This should only happen during training.

## Findings

- `pipeline/feature_engineering.py` line 410: call site inside transform
- `pipeline/feature_engineering.py` lines 419-435: `_save_rubric_csv()` implementation
- Production scoring runs produce unnecessary CSV files as a side effect

## Proposed Solutions

- Remove the `_save_rubric_csv()` call from the `transform()` path
- Call it explicitly during training only (e.g., in a `fit()` or dedicated training script)
