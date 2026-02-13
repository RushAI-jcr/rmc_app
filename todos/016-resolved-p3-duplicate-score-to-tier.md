---
status: resolved
priority: P3
issue_id: 016
tags: [duplication, dead-code]
---

# Duplicate `_score_to_tier()` Function

## Problem Statement

`_score_to_tier()` in `score_pipeline.py` is an exact copy of `score_to_tier()` in `config.py`.

## Findings

- `pipeline/score_pipeline.py`: private `_score_to_tier()` duplicates the public version
- `pipeline/config.py`: canonical `score_to_tier()` already exists
- 6 lines of duplicated code

## Proposed Solutions

- Import `score_to_tier` from `pipeline.config` in `score_pipeline.py`
- Delete the private `_score_to_tier()` copy
