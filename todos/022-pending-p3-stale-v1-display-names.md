---
status: pending
priority: P3
issue_id: 022
tags: [dead-code, config, cleanup]
---

# Stale v1 Display Names and Redundant Aliases

## Problem Statement

`FEATURE_DISPLAY_NAMES` in config contains ~11 entries referencing v1 dimension names that no longer exist, and `_BINARY_ALIASES` in `feature_engineering.py` is redundant with `_fix_known_typos` in `data_preparation.py`.

## Findings

- `pipeline/config.py`: `FEATURE_DISPLAY_NAMES` has ~11 stale v1 dimension name entries
- `pipeline/feature_engineering.py`: `_BINARY_ALIASES` dict overlaps with `_fix_known_typos` in `data_preparation.py`

## Proposed Solutions

- Audit `FEATURE_DISPLAY_NAMES` and remove entries for dimensions that no longer exist in v2
- Remove `_BINARY_ALIASES` and consolidate any needed mappings into `_fix_known_typos`
