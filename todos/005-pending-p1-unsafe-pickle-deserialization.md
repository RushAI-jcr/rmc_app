---
status: pending
priority: p1
issue_id: "005"
tags: [code-review, security, rce]
---

# Unsafe pickle.load / joblib.load — Remote Code Execution Risk

## Problem Statement
`pickle.load()` and `joblib.load()` execute arbitrary code during deserialization. If an attacker substitutes a model file, they gain RCE.

## Findings
- **Locations**: `pipeline/score_pipeline.py` line 124, `pipeline/feature_engineering.py` line 173, `api/services/data_service.py` line 168
- **Agent**: security-sentinel

## Proposed Solutions
1. Add SHA-256 integrity verification for model files
2. Long-term: migrate to safetensors or skops.io
3. For FeaturePipeline: save state as JSON (contains only dicts/lists/floats)

## Acceptance Criteria
- [ ] Model files have integrity verification before loading
- [ ] Hash file generated during training, verified during scoring
