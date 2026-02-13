---
status: pending
priority: P3
issue_id: 018
tags: [dead-code, schema, correctness]
---

# Dead `RubricScores` Model and Incorrect Default

## Problem Statement

`RubricScores` Pydantic model is never used, and `RubricDimension.max_score` defaults to 5.0 despite v2 using a 1-4 scale.

## Findings

- `api/models/applicant.py` lines 37-41: `RubricScores` model defined but never referenced
- `RubricDimension.max_score` defaults to `5.0`, inconsistent with the v2 scoring scale (1-4)

## Proposed Solutions

- Delete the unused `RubricScores` model
- Update `RubricDimension.max_score` default to `4.0` to match the v2 scale
