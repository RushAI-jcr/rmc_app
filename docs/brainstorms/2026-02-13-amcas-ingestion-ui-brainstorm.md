# AMCAS Ingestion UI & Backend Architecture

**Date:** 2026-02-13
**Status:** Brainstorm complete
**Next step:** `/workflows:plan`

---

## What We're Building

A web-based interface for non-technical admissions office staff to upload AMCAS applicant data (multiple Excel files per cycle), preview and validate the parsed data, then trigger the AI triage pipeline -- all without touching code or command-line tools.

### User Flow

```
Staff receives AMCAS export (multiple .xlsx files)
        |
        v
  [Upload Page] -- drag-and-drop or file picker for all required files
        |
        v
  [Preview Page] -- shows parsed applicant count, column validation,
                    warnings (missing fields, format issues), sample rows
        |
        v
  [Approve & Run] -- staff confirms data looks correct, triggers pipeline
        |
        v
  [Pipeline Status] -- polls every 3-5 seconds for progress
        |       (ingestion -> cleaning -> features -> scoring -> triage)
        |
        +---[If failed]--> [Error Details] -- clear error message,
        |                     option to re-upload or retry from same session
        v
  [Results Ready] -- redirect to existing review queue at /review
```

### Target Users

- **Primary:** Admissions office staff (non-technical)
- **Secondary:** Data analyst for monitoring and troubleshooting

---

## Why This Approach

**Chosen: Extend existing FastAPI backend + add PostgreSQL (hybrid storage)**

### Rationale

1. **Fastest path to production** -- Existing FastAPI backend and Python pipeline are already working. Adding upload endpoints and a pipeline orchestration layer is incremental, not a rewrite.

2. **Hybrid storage is pragmatic** -- PostgreSQL handles app state (upload sessions, pipeline runs, user accounts, audit logs) while the ML pipeline continues using CSV/PKL files. This avoids rewriting data_ingestion.py, feature_engineering.py, etc.

3. **Right-sized for the problem** -- ~17,000 applicants/year, small admissions team, 1-2 pipeline runs per cycle. A microservice architecture or serverless setup adds complexity without proportional benefit.

4. **FERPA compliance** -- Single deployment with PostgreSQL gives clear audit trails. Azure deployment with proper access controls and managed services.

### Rejected Alternatives

- **Separate microservice architecture** -- Over-engineered for current scale. Running the pipeline as a second service adds deployment complexity without benefit for 1-2 runs/cycle. (Note: we still use Celery + Redis within the single FastAPI app for async task execution -- the rejection was of a separate service, not Celery itself.)
- **Next.js full-stack + serverless** -- Splits backend across TypeScript and Python runtimes. Would abandon or duplicate the existing FastAPI work.

---

## Key Decisions

1. **Extend FastAPI** -- Add new routers for ingestion, not a separate service
2. **PostgreSQL for app state** -- Pipeline runs, upload sessions, auth, audit logs. Use Alembic for schema migrations.
3. **Keep CSV/PKL for ML** -- Pipeline reads/writes files as-is; no rewrite
4. **Celery + Redis for pipeline jobs** -- Pipeline runs take minutes for 17K applicants; Celery provides retries, monitoring, and survives server restarts. Worth the added dependency at this scale.
5. **Simple auth** -- Login wall with session-based auth (JWT in httpOnly cookie). Accounts seeded by a developer via CLI/script (no registration flow). Add a `role` column to users table (default: "staff") to future-proof for roles.
6. **Azure deployment** -- Azure App Service for the app, Azure Database for PostgreSQL, Azure Blob Storage for uploaded files, Azure Cache for Redis
7. **Upload -> Preview -> Approve -> Run** -- Multi-step workflow giving staff control before AI processing
8. **Polling for progress** -- Frontend polls `/api/pipeline/runs/{id}` every 3-5 seconds. Simpler than SSE, acceptable UX for a process that runs 1-2 times per cycle.
9. **One cycle at a time** -- Enforced at the application level: approve endpoint checks for any active `pipeline_runs` and rejects if one is running. `upload_sessions` table has an `is_active` flag.
10. **Azure Blob Storage for uploads** -- Uploaded Excel files stored in Blob Storage (durable, FERPA-appropriate), pipeline orchestrator downloads to temp dir for processing. Retention policy: 3 years, then auto-deleted.

---

## Backend Components Needed

### New FastAPI Routers

| Router | Endpoints | Purpose |
|--------|-----------|---------|
| `ingest.py` | `POST /api/ingest/upload` | Accept multiple Excel files, upload to Blob Storage |
| | `GET /api/ingest/sessions` | List past upload sessions (history view) |
| | `GET /api/ingest/{session_id}/preview` | Return parsed data summary, validation warnings |
| | `POST /api/ingest/{session_id}/approve` | Validate no active run, then trigger pipeline via Celery |
| | `POST /api/ingest/{session_id}/retry` | Re-trigger pipeline from a failed session |
| `pipeline_status.py` | `GET /api/pipeline/runs` | List all pipeline runs with status |
| | `GET /api/pipeline/runs/{run_id}` | Detailed status of a specific run (polled by frontend) |
| `auth.py` | `POST /api/auth/login` | Authenticate, return JWT in httpOnly cookie |
| | `POST /api/auth/logout` | Clear session cookie |

### New Services

| Service | Responsibility |
|---------|---------------|
| `upload_service.py` | File validation against expected schemas, Blob Storage upload, session management |
| `pipeline_orchestrator.py` | Celery task that wraps existing pipeline steps, updates `pipeline_runs` with progress, handles errors |
| `auth_service.py` | JWT generation/validation, password hashing with bcrypt |

### Existing Pipeline Interface

The orchestrator calls existing pipeline modules as Python functions:

| Module | Location | Input | Output |
|--------|----------|-------|--------|
| `data_ingestion.py` | `pipeline/` | Excel file paths (downloaded from Blob) | Merged DataFrame |
| `data_cleaning.py` | `pipeline/` | Raw DataFrame | Cleaned DataFrame |
| `feature_engineering.py` | `pipeline/` | Cleaned DataFrame | Feature matrix (CSV) |
| `model_training.py` | `pipeline/` | Feature matrix | Predictions + SHAP (PKL) |
| `model_evaluation.py` | `pipeline/` | Predictions | Metrics, tier assignments |

The orchestrator imports these modules and calls their main functions sequentially, updating `pipeline_runs.current_step` and `progress_pct` after each step completes.

### Database Schema (PostgreSQL, managed via Alembic)

```
upload_sessions
  - id (UUID, PK)
  - created_at, updated_at (timestamptz)
  - uploaded_by (FK -> users.id)
  - cycle_year (int)
  - is_active (bool, default false) -- only one active session at a time
  - file_manifest (JSONB -- list of uploaded files with sizes/types/blob paths)
  - validation_result (JSONB -- warnings, errors, parsed counts)
  - status (uploaded | validated | approved | processing | complete | failed)

pipeline_runs
  - id (UUID, PK)
  - upload_session_id (FK -> upload_sessions.id)
  - started_at, completed_at (timestamptz, nullable)
  - current_step (ingestion | cleaning | features | scoring | triage)
  - progress_pct (int, 0-100)
  - result_summary (JSONB -- applicant count, tier distribution)
  - error_log (text, nullable)
  - status (pending | running | complete | failed)

users
  - id (UUID, PK)
  - username (varchar, unique)
  - password_hash (varchar)
  - role (varchar, default 'staff') -- future-proofing for admin/reviewer roles
  - created_at (timestamptz)
  - last_login (timestamptz, nullable)
```

### New Frontend Pages

| Page | Purpose |
|------|---------|
| `/login` | Simple login page |
| `/ingest` | Upload wizard -- drag-and-drop for AMCAS Excel files, plus session history list |
| `/ingest/[sessionId]/preview` | Data preview with validation warnings, approve button |
| `/ingest/[sessionId]/status` | Pipeline progress tracker (polls every 3-5s), error display with retry option |

### New Dependencies

| Package | Purpose |
|---------|---------|
| `celery[redis]` | Async task queue for pipeline jobs |
| `sqlalchemy` + `alembic` | ORM + database migrations |
| `azure-storage-blob` | Upload/download files to Azure Blob Storage |
| `pyjwt` + `bcrypt` | Auth (JWT tokens + password hashing) |
| `psycopg2-binary` | PostgreSQL driver |

### Local Development

Docker Compose for local development:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Celery worker (runs pipeline tasks)
- FastAPI app (port 8000)
- Next.js frontend (port 3000)

---

## AMCAS File Expectations

Based on the existing pipeline, each cycle requires these Excel files:

| File | Required? | Contains | Key Columns |
|------|-----------|----------|-------------|
| Applicants | Yes | Main applicant table | AMCAS_ID, demographics, reviewer scores |
| Experiences | Yes | 1-to-many per applicant | AMCAS_ID, Experience_Type, Hours |
| Personal Statement | Yes | Essay text | AMCAS_ID, statement text |
| Secondary Applications | No | Secondary essay responses | AMCAS_ID, responses |
| GPA Trends | Yes | Academic performance | AMCAS_ID, GPA by year |
| Languages | No | Languages spoken | AMCAS_ID, language list |
| Parents | No | Parent education level | AMCAS_ID, education ordinal |

**Validation rules:**
- All required files must be present before approval
- Each file must contain its key columns (column name matching)
- Applicants file must have > 100 rows (sanity check against accidental partial uploads)
- All files must share a common set of AMCAS_IDs (cross-file join check)
- Files must be .xlsx format

---

## Resolved Questions

1. **Task queue choice** -- **Celery + Redis.** Pipeline runs take minutes for 17K applicants. Celery provides retries, monitoring via Flower, and survives server restarts. Redis is lightweight and Azure Cache for Redis is managed.

2. **Cloud provider** -- **Azure.** Aligns with institutional requirements. Azure App Service + Azure Database for PostgreSQL + Azure Blob Storage + Azure Cache for Redis.

3. **Real-time progress updates** -- **Polling every 3-5 seconds.** Pipeline runs 1-2 times per cycle, so the slight delay is acceptable and implementation is much simpler than SSE/WebSockets.

4. **File storage during processing** -- **Azure Blob Storage.** Durable, FERPA-appropriate, and the pipeline orchestrator downloads files to a temp directory for processing. 3-year retention policy, then auto-deleted.

5. **Cycle management** -- **One active cycle at a time.** Enforced by application logic (check for active runs before starting new ones). Historical cycle data retained and viewable.

---

## Success Criteria

- Admissions staff can upload a new cycle's AMCAS files without developer assistance
- Data validation catches common issues (missing columns, wrong file format, missing files) before pipeline runs
- Pipeline progress is visible via polling (updates every 3-5 seconds)
- Failed runs show clear, non-technical error messages and offer retry or re-upload options
- Complete audit trail of who uploaded what and when (FERPA)
- End-to-end time from upload to triage results is under 15 minutes
