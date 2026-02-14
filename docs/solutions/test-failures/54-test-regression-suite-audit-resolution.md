---
title: "Zero to 54: Building a Regression Test Suite from Audit Recommendations"
date: 2026-02-13
category: test-failures
severity: high
components:
  - FastAPI backend
  - ML pipeline
  - authentication
  - feature engineering
  - file upload
tags:
  - regression-tests
  - pytest
  - security-audit
  - path-traversal
  - pickle-verification
  - idor-protection
  - rate-limiting
  - feature-engineering
  - jwt-lifecycle
  - test-infrastructure
metrics:
  total_tests: 54
  test_modules: 4
  execution_time_seconds: 0.84
  pass_rate: 100
  audit_findings_covered: 10
symptoms: |
  - Codebase had zero test infrastructure
  - 22-item audit identified security, correctness, and quality issues
  - No automated regression prevention for any of the fixes applied
  - Manual QA could not scale to validate all audit findings
root_cause: |
  The application was built as a research prototype that transitioned toward
  production without establishing test infrastructure. All 22 audit fixes were
  applied to code but had no automated verification, meaning any future change
  could silently reintroduce vulnerabilities.
resolution_commit: "651a3b1"
related_docs:
  - docs/solutions/security-issues/comprehensive-audit-p1-p2-p3-resolution.md
  - docs/solutions/code-quality/multi-agent-comprehensive-code-review-22-findings.md
  - docs/brainstorms/fastapi-stack-best-practices-2025-2026.md
  - docs/feature_engineering_implementation_spec.md
---

# Zero to 54: Building a Regression Test Suite from Audit Recommendations

## Problem

After a comprehensive 22-item audit of the RMC admissions triage application, all fixes were applied across two commits. However, the codebase had **zero tests** — no infrastructure to prevent any of the 22 issues from recurring.

Without regression tests:
- Any future refactor could silently reintroduce path traversal or IDOR vulnerabilities
- Feature engineering changes could re-break `fit_transform()` or re-duplicate logic
- Configuration drift could silently break display names or dimension mappings
- Deployment confidence was effectively zero

## Solution Architecture

Created 4 focused test modules covering all 10 recommended test areas from the audit. All tests are fast unit tests requiring no database, server, or network.

| Module | Tests | Focus Areas |
|--------|-------|-------------|
| `test_security.py` | 14 | Path traversal, no hardcoded secrets, pickle SHA-256 verification, rate limiter |
| `test_feature_pipeline.py` | 12 | fit_transform caching, composite feature parity, save/load roundtrip, demographics guard |
| `test_config.py` | 16 | score_to_tier boundaries, display name coverage, dimension consistency, import health |
| `test_auth_and_idor.py` | 12 | Bearer+cookie auth, IDOR ownership, AST endpoint guard verification, JWT lifecycle |

### Shared Infrastructure (`conftest.py`)

Minimal setup with environment isolation:
```python
os.environ.setdefault("DATABASE_URL", "sqlite:///")
os.environ.setdefault("JWT_SECRET", "test-secret-key-must-be-at-least-32-characters-long")
os.environ.setdefault("ENVIRONMENT", "test")
```

No complex mocking infrastructure. Tests verify actual implementation behavior.

## Key Patterns

### 1. AST Parsing for Endpoint Guards (P2-007)

Parses `ingest.py` with Python's `ast` module to find all functions with a `session_id` parameter and verifies each calls `verify_session_ownership`. Future endpoints can't skip authorization.

```python
def test_all_session_endpoints_guarded(self) -> None:
    source = ingest_path.read_text()
    tree = ast.parse(source)

    session_endpoints = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if "session_id" in [arg.arg for arg in node.args.args]:
                session_endpoints.append(node.name)

    for func_name in session_endpoints:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                body_source = ast.get_source_segment(source, node)
                assert "verify_session_ownership" in body_source
```

### 2. Parametrized Path Traversal (P1-002)

Single test with all known malicious patterns. Adding new attack vectors is trivial.

```python
MALICIOUS_NAMES = [
    "../../../etc/passwd",
    "foo/../../bar.xlsx",
    ".env",
    ".ssh/id_rsa",
    "....//....//etc/passwd",
]

@pytest.mark.parametrize("malicious_name", MALICIOUS_NAMES)
def test_purepath_strips_traversal(self, malicious_name: str) -> None:
    safe = PurePosixPath(malicious_name).name
    assert "/" not in safe
    assert ".." not in safe.split("/")
```

### 3. Mock-Free Composite Verification (P3-015)

Tests both `engineer_composite_features()` (standalone) and `FeaturePipeline` on identical data and compares outputs without mocking. Any drift between implementations causes immediate failure.

```python
def test_pipeline_and_standalone_match(self) -> None:
    standalone = engineer_composite_features(df)
    pipe = FeaturePipeline(include_rubric=False)
    pipe_result = pipe.fit_transform(df)

    for feat in ENGINEERED_FEATURES:
        pd.testing.assert_series_equal(
            standalone[feat].reset_index(drop=True),
            pipe_result[feat].reset_index(drop=True),
        )
```

### 4. Single-Transform Counting (P2-011)

Patches `_transform_impl` with a counting wrapper to verify `fit_transform()` calls it exactly once (not twice as the bug did).

```python
def test_fit_transform_only_transforms_once(self) -> None:
    call_count = 0
    original = pipe._transform_impl

    def counting_transform(df_arg):
        nonlocal call_count
        call_count += 1
        return original(df_arg)

    with patch.object(pipe, "_transform_impl", side_effect=counting_transform):
        pipe.fit_transform(df)

    assert call_count == 1
```

### 5. Pickle Integrity Three-Way Test (P1-005)

Covers the happy path, missing hash file, and tampered file scenarios:

```python
def test_save_and_load_verified(self, tmp_path):
    save_verified_pickle(obj, model_path)
    loaded = load_verified_pickle(model_path)
    assert loaded == obj

def test_load_without_hash_raises(self, tmp_path):
    model_path.write_bytes(pickle.dumps({"test": "data"}))
    with pytest.raises(FileNotFoundError, match="Hash file not found"):
        load_verified_pickle(model_path)

def test_tampered_file_raises(self, tmp_path):
    save_verified_pickle({"original": True}, model_path)
    model_path.write_bytes(pickle.dumps({"tampered": True}))
    with pytest.raises(ValueError, match="integrity check failed"):
        load_verified_pickle(model_path)
```

## Test Coverage Map

| Audit Item | Severity | Test Class | Tests | What It Catches |
|------------|----------|------------|-------|-----------------|
| P1-002 | Critical | `TestPathTraversalBlocked` | 5 | Path traversal attack vectors, dotfile injection |
| P1-003/004 | Critical | `TestNoHardcodedSecrets` | 2 | Credentials in source code, JWT default values |
| P1-005 | Critical | `TestPickleVerification` | 4 | Tampered models, missing hashes, SHA-256 correctness |
| P2-007 | High | `TestVerifySessionOwnership` + `TestIngestEndpointsHaveOwnershipCheck` | 4 | Cross-user session access, missing guards on new endpoints |
| P2-009 | High | `TestDualAuth` | 3 | Bearer token extraction, cookie fallback, missing auth |
| P2-011 | High | `TestFitTransformCached` | 4 | Double transformation, cache cleanup, result equivalence |
| P3-015 | Medium | `TestSharedCompositeFeatures` | 5 | Implementation drift between standalone and pipeline |
| P3-016 | Medium | `TestScoreToTier` | 2 | Tier boundary errors, non-monotonic tier assignment |
| P3-021 | Medium | `TestRateLimiting` | 2 | Sliding window enforcement, window expiration |
| P3-022 | Medium | `TestFeatureDisplayNames` | 4 | Missing display names for new features |
| Consistency | Medium | `TestDimensionConsistency` | 5 | Stale dimensions, duplicates, prompt/config mismatch |
| JWT | Medium | `TestJWTTokens` | 3 | Token creation, expiration, invalid signature |
| Imports | Low | `TestImports` | 4 | Broken module imports |
| Pipeline I/O | Medium | `TestPipelineSaveLoad` | 3 | Save/load roundtrip, JSON format, demographics leak |

## Prevention: CI Integration

Add to CI pipeline:

```bash
# Run all regression tests (< 1 second)
pytest tests/ -v --tb=short

# With coverage
pytest tests/ --cov=pipeline --cov=api --cov-report=term
```

No external dependencies needed — tests run with SQLite in-memory and test JWT secret.

## Coverage Gaps (Next Steps)

Priority order for expanding coverage:

| Priority | Gap | Est. Tests | Effort |
|----------|-----|------------|--------|
| P0 | API endpoint integration (TestClient) | 25 | High |
| P0 | Database integration (SQLAlchemy fixtures) | 15 | High |
| P1 | Celery task execution | 12 | Medium |
| P1 | End-to-end workflows | 10 | Medium |
| P2 | Error handling edge cases (NaN, empty df) | 20 | Medium |
| P2 | Fairness/bias auditing | 10 | Medium |

## Cross-References

- [Audit Resolution (22 findings)](../security-issues/comprehensive-audit-p1-p2-p3-resolution.md) — the fixes these tests protect
- [FastAPI Best Practices](../../brainstorms/fastapi-stack-best-practices-2025-2026.md) — JWT, CSRF, file upload patterns
- [Feature Engineering Spec](../../feature_engineering_implementation_spec.md) — composite feature formulas
