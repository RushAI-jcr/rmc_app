---
title: Comprehensive Security and Quality Audit Resolution (22 Issues)
date: 2026-02-13
category: security-issues
severity: critical
components:
  - FastAPI backend
  - Next.js frontend
  - ML pipeline
  - authentication
  - file upload
  - Celery tasks
  - feature engineering
tags:
  - security-audit
  - path-traversal
  - jwt-secrets
  - pickle-verification
  - idor
  - rate-limiting
  - data-leakage
  - feature-engineering
  - performance
  - dead-code
symptoms: |
  - Broken import statements causing module resolution failures
  - Path traversal vulnerability in file upload endpoint
  - Hardcoded JWT secrets and database credentials
  - Unsafe pickle deserialization (RCE risk)
  - Database unique constraint blocking pipeline retries
  - Missing IDOR protection on session endpoints
  - Cookie-only auth blocking programmatic access
  - fit_transform() crash from missing cached result
  - Duplicate feature engineering logic across modules
  - iterrows() performance bottleneck in data preparation
  - No rate limiting on login endpoint
  - Missing security headers (HSTS, X-Frame-Options)
root_cause: |
  Initial development prioritized feature completion over security hardening.
  The codebase started as a research prototype where default credentials and
  missing validation were acceptable locally but became vulnerabilities when
  moving to production. Parallel development of API and pipeline teams led to
  code duplication without cross-team review. No systematic audit was performed
  before production readiness.
resolution_commits:
  - "fix(security): resolve all 6 P1 audit findings"
  - "fix: resolve all P2/P3 audit findings (16 items)"
related_docs:
  - docs/brainstorms/fastapi-stack-best-practices-2025-2026.md
  - docs/plans/2026-02-13-feat-amcas-ingestion-ui-plan.md
  - docs/plans/2026-02-13-feat-azure-foundry-llm-pipeline-plan.md
  - docs/feature_engineering_implementation_spec.md
  - infra/README.md
---

# Comprehensive Security and Quality Audit Resolution

## Problem Summary

A 22-item audit of the RMC admissions triage application identified issues across three priority levels. All items have been resolved.

| Priority | Count | Category | Examples |
|----------|-------|----------|----------|
| P1 (Critical) | 6 | Security | Path traversal, hardcoded secrets, unsafe pickle, broken imports |
| P2 (Medium) | 8 | Correctness | IDOR, data leakage, auth gaps, fit_transform crash, Celery timeouts |
| P3 (Low) | 8 | Quality | Duplicate code, iterrows performance, dead code, rate limiting |

## Code Fixes Applied

### 1. Rate Limiting on Login Endpoint (P3-021)

**File:** `api/routers/auth.py`

**Problem:** No rate limiting allowed brute-force password attacks.

**Fix:** Added in-memory IP-based rate limiter (5 attempts per 60 seconds):

```python
_login_attempts: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 5
_RATE_WINDOW = 60

@router.post("/login")
def login(body: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    _login_attempts[client_ip] = [t for t in _login_attempts[client_ip] if now - t < _RATE_WINDOW]
    if len(_login_attempts[client_ip]) >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")
    _login_attempts[client_ip].append(now)
    # ... rest of login
```

### 2. Deduplicated Feature Engineering (P3-015)

**Files:** `pipeline/feature_engineering.py`, `api/services/data_service.py`

**Problem:** 87 lines of composite feature logic duplicated between `DataStore` and `FeaturePipeline`. Formula changes required updating both locations.

**Fix:** Extracted `engineer_composite_features()` as a shared module-level function. Both `FeaturePipeline._engineer_composites()` and `DataStore._compute_engineered_features()` now delegate to it:

```python
# pipeline/feature_engineering.py (module-level)
def engineer_composite_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute 7 reviewer-aligned composite features.
    Shared by FeaturePipeline (training/scoring) and DataStore (API startup)."""
    # Total_Volunteer_Hours, Community_Engaged_Ratio, Clinical_Total_Hours,
    # Direct_Care_Ratio, Adversity_Count, Grit_Index, Experience_Diversity
    ...

# api/services/data_service.py
from pipeline.feature_engineering import engineer_composite_features

def _compute_engineered_features(self) -> None:
    if "Total_Volunteer_Hours" not in df.columns:
        composites = engineer_composite_features(df)
        for col in composites.columns:
            if col != ID_COLUMN:
                df[col] = composites[col]
    # Only API-specific normalization remains (30 lines instead of 87)
```

### 3. Fixed fit_transform Double Transform (P2-011)

**File:** `pipeline/feature_engineering.py`

**Problem:** `fit_transform()` called `fit()` then `transform()`, running `_transform_impl()` twice on training data.

**Fix:** Cache the transform result during `fit()` so `fit_transform()` reuses it:

```python
def fit(self, df: pd.DataFrame) -> "FeaturePipeline":
    # ... learning logic ...
    features_df = self._transform_impl(df)
    self._fitted_transform_result = features_df  # Cache for fit_transform()
    self.feature_columns_ = [c for c in features_df.columns if c != ID_COLUMN]
    self.is_fitted_ = True
    return self

def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
    self.fit(df)
    result = self._fitted_transform_result
    self._fitted_transform_result = None  # Free memory
    return result[[ID_COLUMN] + self.feature_columns_]
```

### 4. Replaced iterrows with Vectorized Operations (P3-019)

**File:** `pipeline/data_preparation.py`

**Problem:** `build_secondary_texts_dict()` used `.iterrows()`, which is ~100x slower than vectorized approaches.

**Fix:** Replaced with `.apply()` and vectorized dict creation:

```python
def _concat_essays(row: pd.Series) -> str:
    parts = []
    for col in essay_cols:
        val = row[col]
        if pd.notna(val) and str(val).strip():
            prompt_name = col.replace("_", " ").strip()
            parts.append(f"[{prompt_name}]\n{str(val).strip()}")
    return "\n\n---\n\n".join(parts)

sec_df["_combined"] = sec_df[essay_cols].apply(_concat_essays, axis=1)
valid = sec_df["_combined"].str.len() > 0
result = dict(zip(
    sec_df.loc[valid, ID_COLUMN].astype(int),
    sec_df.loc[valid, "_combined"],
))
```

### 5. Security Headers and CORS Restrictions (P3-021, already applied)

**File:** `api/main.py`

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "POST", "PATCH"],  # Was ["*"]
    allow_headers=["Content-Type", "Authorization"],  # Was ["*"]
)
```

### 6. Path Traversal Protection (P1-002, already applied)

**File:** `api/services/upload_service.py`

Multi-layer defense: sanitize filename with `PurePosixPath(name).name`, reject dotfiles, verify resolved path is within session directory via `.resolve().is_relative_to()`.

### 7. Pickle Integrity Verification (P1-005, already applied)

**File:** `pipeline/model_verification.py`

SHA-256 hash verification before deserializing pickle files. Models must be saved with `save_verified_pickle()` to generate `.sha256` companion files.

### 8. JWT Secret Hardening (P1-003, already applied)

**File:** `api/settings.py`

Removed default JWT secret. Application fails fast on startup if secret is missing or under 32 characters in production.

### 9. IDOR Protection (P2-007, already applied)

**File:** `api/routers/ingest.py`

`verify_session_ownership()` called on all 5 session endpoints. Only session owner or admin can access.

### 10. Bearer + Cookie Auth (P2-009, already applied)

**File:** `api/dependencies.py`

`Authorization: Bearer <token>` header tried first, httpOnly cookie fallback for browsers.

### 11. Celery Task Time Limits (P2-013, already applied)

**File:** `api/tasks/pipeline_task.py`

`soft_time_limit=300` (5 min graceful) + `time_limit=360` (6 min hard kill) with `SoftTimeLimitExceeded` handler.

## Items Already Resolved in Prior Commits

| Issue | Status | Notes |
|-------|--------|-------|
| P1-001: Broken API imports | Fixed in `a14d21d` | v2 dimension names imported correctly |
| P1-004: Hardcoded credentials | Fixed in `515d04d` | `.env.example` with placeholders |
| P1-006: Unique constraint retry | Fixed in schema design | Partial index allows retries |
| P2-008: On-the-fly fit | Fixed | `score_pipeline` raises `FileNotFoundError` |
| P2-010: Double xlsx read | Fixed | Single read + `.head(5)` for preview |
| P2-012: Stale v1 rubric groups | Fixed | RUBRIC_GROUPS uses v2 keys |
| P2-014: Non-monotonic progress | Fixed | Progress percentages monotonically increase |
| P3-016: Duplicate score_to_tier | Fixed | Single function in `pipeline/config.py` |
| P3-017: Rubric CSV side effect | Fixed | No intermediate CSV writes |
| P3-018: Dead rubric_scores model | Fixed | Removed, `max_score=4.0` |
| P3-020: Legacy type hints | Fixed | Modern `X \| None` syntax throughout |
| P3-022: Stale display names | Fixed | Updated to v2 dimension names |

## Prevention Checklist

Use before merging any PR to main:

### Security
- [ ] No hardcoded secrets -- all from environment variables via `settings`
- [ ] File uploads sanitize filenames with `PurePosixPath(name).name` + `.is_relative_to()` check
- [ ] All pickle loading uses `load_verified_pickle()` from `model_verification`
- [ ] All imports resolve cleanly (`python -c "import api; import pipeline"`)
- [ ] No database credentials in source code

### Correctness
- [ ] All session endpoints check ownership via `verify_session_ownership()`
- [ ] Auth supports both Bearer header and httpOnly cookie
- [ ] `FeaturePipeline.fit()` never called during scoring -- only `transform()`
- [ ] Excel files read exactly once per operation
- [ ] All Celery tasks have `soft_time_limit` and `time_limit`
- [ ] Progress percentages never decrease

### Quality
- [ ] Feature engineering logic exists in one place (`engineer_composite_features()`)
- [ ] No `.iterrows()` in hot paths -- use `.apply()` or vectorized ops
- [ ] Modern type hints (`dict[str, str]` not `Dict[str, str]`)
- [ ] `FEATURE_DISPLAY_NAMES` matches all feature columns

## Architecture Guidelines

### Secret Management
```python
# Correct: from environment
from api.settings import settings
jwt_secret = settings.jwt_secret  # From JWT_SECRET env var

# Wrong: hardcoded fallback
jwt_secret = os.getenv("JWT_SECRET", "insecure-default")  # Never
```

### ML Pipeline (Leakage Prevention)
```python
# Training: fit_transform() once
features = pipeline.fit_transform(train_df)
pipeline.save(path)

# Scoring: load() then transform() only -- never fit()
pipeline = FeaturePipeline.load(path)
features = pipeline.transform(new_df)
```

### File Upload Safety
```python
safe_name = PurePosixPath(filename).name
if safe_name.startswith('.'):
    raise ValueError("Rejected")
dest = session_dir / safe_name
if not dest.resolve().is_relative_to(session_dir.resolve()):
    raise ValueError("Path traversal attempt")
```

### Rate Limiting Pattern
```python
_attempts: dict[str, list[float]] = defaultdict(list)

def rate_limit_check(client_ip: str, max_attempts=5, window=60):
    now = time.monotonic()
    _attempts[client_ip] = [t for t in _attempts[client_ip] if now - t < window]
    if len(_attempts[client_ip]) >= max_attempts:
        raise HTTPException(status_code=429)
    _attempts[client_ip].append(now)
```

## Testing Recommendations

### Priority Test Cases to Add

1. **Path traversal blocked** -- malicious filenames (`../../../etc/passwd`) rejected
2. **No hardcoded secrets in code** -- grep repo for credential patterns
3. **IDOR prevented** -- User A cannot access User B's sessions (expect 403)
4. **Bearer + Cookie auth** -- both paths return 200
5. **No data leakage** -- `FeaturePipeline.fit()` not called during `score_new_cycle()`
6. **Monotonic progress** -- progress percentages never decrease
7. **Feature engineering parity** -- DataStore and FeaturePipeline produce identical features
8. **Pickle integrity enforced** -- loading without `.sha256` file raises `FileNotFoundError`
9. **Rate limiting works** -- 6th login attempt within 60s returns 429
10. **Celery timeout handled** -- tasks exceeding 5 min produce user-friendly error

### Automated CI Checks

- `bandit -ll api/ pipeline/` -- detect hardcoded secrets
- `mypy --strict api/ pipeline/` -- type safety
- `grep -r "pickle.load" api/ pipeline/` -- ensure `load_verified_pickle` used
- `python -c "import api; import pipeline"` -- import validation

## Cross-References

- [FastAPI Best Practices](../../brainstorms/fastapi-stack-best-practices-2025-2026.md) -- JWT patterns, CSRF, file upload
- [AMCAS Ingestion UI Plan](../../plans/2026-02-13-feat-amcas-ingestion-ui-plan.md) -- 7 critical security findings
- [Azure Foundry LLM Pipeline Plan](../../plans/2026-02-13-feat-azure-foundry-llm-pipeline-plan.md) -- pickle risks, FERPA
- [Feature Engineering Spec](../../feature_engineering_implementation_spec.md) -- composite feature formulas
- [Infrastructure README](../../infra/README.md) -- deployment security (TLS, Key Vault)
