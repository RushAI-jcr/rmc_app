---
status: resolved
priority: P3
issue_id: 015
tags: [duplication, feature-engineering, maintainability]
---

# Duplicate Feature Engineering Logic

## Problem Statement

`DataStore._compute_engineered_features()` (87 lines) duplicates `FeaturePipeline._engineer_composites()` (55 lines), creating a maintenance hazard where formula changes must be applied in two places.

## Findings

- `api/services/data_service.py` lines 75-161: `_compute_engineered_features()` (87 lines)
- `pipeline/feature_engineering.py` lines 258-312: `_engineer_composites()` (55 lines)
- Both compute the same derived features with slightly different implementations

## Proposed Solutions

- Have `DataStore` call `FeaturePipeline._engineer_composites()` instead of reimplementing the logic
- Alternatively, extract shared formulas into a standalone utility module that both classes import
