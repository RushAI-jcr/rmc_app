# FastAPI Stack Best Practices (2025-2026)

Comprehensive research covering FastAPI + Celery, file uploads, JWT auth, SQLAlchemy 2.0, and Azure Blob Storage.

---

## 1. FastAPI + Celery Integration

### 1.1 Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py             # Settings
│   ├── celery_app.py         # Celery instance
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── file_tasks.py     # File processing tasks
│   │   └── email_tasks.py    # Email tasks
│   ├── api/
│   │   └── routes.py
│   └── db/
│       └── session.py
├── celery_worker.py           # Worker entry point
└── requirements.txt
```

### 1.2 Celery App Configuration

```python
# app/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,       # e.g. "redis://localhost:6379/0"
    backend=settings.CELERY_RESULT_BACKEND,   # e.g. "redis://localhost:6379/1"
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task execution limits
    task_soft_time_limit=300,    # 5 min soft limit (raises SoftTimeLimitExceeded)
    task_time_limit=360,         # 6 min hard kill

    # Task result expiry
    result_expires=3600,         # Results expire after 1 hour

    # Worker settings
    worker_prefetch_multiplier=1,     # Fetch one task at a time (fair scheduling)
    worker_max_tasks_per_child=200,   # Restart worker after 200 tasks (prevent memory leaks)
    worker_max_memory_per_child=200_000,  # 200MB memory limit per worker

    # Task routing (optional)
    task_routes={
        "app.tasks.file_tasks.*": {"queue": "file_processing"},
        "app.tasks.email_tasks.*": {"queue": "emails"},
    },

    # Late acknowledgment -- task is acked after completion, not before
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Auto-discover tasks from the tasks package
celery_app.autodiscover_tasks(["app.tasks"])
```

### 1.3 Task Definitions with Retries, Timeouts, and Progress

```python
# app/tasks/file_tasks.py
import time
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,          # Exponential backoff: 1s, 2s, 4s, ...
    retry_backoff_max=600,       # Cap backoff at 10 minutes
    retry_jitter=True,           # Add randomness to prevent thundering herd
    acks_late=True,
    track_started=True,
    name="app.tasks.file_tasks.process_uploaded_file",
)
def process_uploaded_file(self, file_path: str, user_id: int) -> dict:
    """Process an uploaded file with progress tracking and retry logic.

    Design principles:
    - IDEMPOTENT: Safe to run multiple times with the same inputs.
    - Uses bind=True to access self (task instance) for state updates.
    - Reports progress via self.update_state() so the API can poll status.
    """
    total_steps = 5

    try:
        # Step 1: Validate file
        self.update_state(
            state="PROGRESS",
            meta={"current": 1, "total": total_steps, "status": "Validating file..."},
        )
        _validate_file(file_path)

        # Step 2: Parse contents
        self.update_state(
            state="PROGRESS",
            meta={"current": 2, "total": total_steps, "status": "Parsing contents..."},
        )
        parsed = _parse_file(file_path)

        # Step 3: Transform data
        self.update_state(
            state="PROGRESS",
            meta={"current": 3, "total": total_steps, "status": "Transforming data..."},
        )
        transformed = _transform(parsed)

        # Step 4: Store results
        self.update_state(
            state="PROGRESS",
            meta={"current": 4, "total": total_steps, "status": "Storing results..."},
        )
        _store_results(transformed, user_id)

        # Step 5: Cleanup
        self.update_state(
            state="PROGRESS",
            meta={"current": 5, "total": total_steps, "status": "Cleaning up..."},
        )
        _cleanup(file_path)

        return {
            "status": "completed",
            "user_id": user_id,
            "records_processed": len(transformed),
        }

    except SoftTimeLimitExceeded:
        logger.warning("Task %s hit soft time limit", self.request.id)
        _cleanup(file_path)
        return {"status": "timeout", "error": "Processing took too long"}

    except (ConnectionError, TimeoutError) as exc:
        # These are auto-retried via autoretry_for, but we can add logging
        logger.warning(
            "Transient error in task %s (attempt %d/%d): %s",
            self.request.id,
            self.request.retries,
            self.max_retries,
            exc,
        )
        raise  # Let autoretry handle it

    except ValueError as exc:
        # Permanent failure -- do NOT retry
        logger.error("Permanent failure in task %s: %s", self.request.id, exc)
        return {"status": "failed", "error": str(exc)}


@shared_task(
    bind=True,
    max_retries=5,
    name="app.tasks.file_tasks.send_notification",
)
def send_notification(self, user_id: int, message: str) -> dict:
    """Example with manual exponential backoff."""
    try:
        _send_push(user_id, message)
        return {"status": "sent"}
    except ConnectionError as exc:
        # Manual exponential backoff: 5s, 10s, 20s, 40s, 80s
        retry_in = 5 * (2 ** self.request.retries)
        logger.warning(
            "Notification failed, retrying in %ds (attempt %d/%d)",
            retry_in,
            self.request.retries + 1,
            self.max_retries,
        )
        raise self.retry(exc=exc, countdown=retry_in)
```

### 1.4 FastAPI Endpoints -- Submit Tasks and Poll Progress

```python
# app/api/routes.py
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.tasks.file_tasks import process_uploaded_file

router = APIRouter()


@router.post("/tasks/process-file")
async def create_file_task(file_path: str, user_id: int):
    """Submit a file processing task and return the task ID immediately."""
    task = process_uploaded_file.delay(file_path, user_id)
    return {"task_id": task.id, "status": "queued"}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Poll task status and progress."""
    result = AsyncResult(task_id, app=celery_app)

    if result.state == "PENDING":
        return {"task_id": task_id, "status": "pending", "progress": 0}

    elif result.state == "PROGRESS":
        return {
            "task_id": task_id,
            "status": "processing",
            "current": result.info.get("current", 0),
            "total": result.info.get("total", 1),
            "detail": result.info.get("status", ""),
            "progress": int(
                (result.info.get("current", 0) / result.info.get("total", 1)) * 100
            ),
        }

    elif result.state == "SUCCESS":
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result.result,
            "progress": 100,
        }

    elif result.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(result.info),
            "progress": 0,
        }

    else:
        return {"task_id": task_id, "status": result.state}


@router.post("/tasks/{task_id}/revoke")
async def revoke_task(task_id: str):
    """Cancel a running or pending task."""
    celery_app.control.revoke(task_id, terminate=True, signal="SIGTERM")
    return {"task_id": task_id, "status": "revoked"}
```

### 1.5 Sharing Database Sessions Between Web and Worker

**Critical rule: Celery workers run in separate processes. Never share SQLAlchemy sessions or engines across the process boundary.**

```python
# app/db/session.py
"""
Database session factories for both FastAPI (async) and Celery (sync).

FastAPI uses async sessions via dependency injection.
Celery uses sync sessions created per-task.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

# --- Async engine for FastAPI ---
async_engine = create_async_engine(
    settings.DATABASE_URL,       # e.g. "postgresql+asyncpg://..."
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncSession:
    """FastAPI dependency: yields one async session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# --- Sync engine for Celery workers ---
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,  # e.g. "postgresql+psycopg2://..."
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_sync_db() -> Session:
    """Celery task helper: returns a sync session. Caller must close it."""
    return SyncSessionLocal()
```

```python
# app/tasks/file_tasks.py -- using sync sessions in Celery tasks
from app.db.session import get_sync_db

@shared_task(bind=True, max_retries=3)
def store_records(self, records: list[dict]) -> dict:
    """Celery task that writes to the database with proper session handling."""
    db = get_sync_db()
    try:
        for record in records:
            db.add(MyModel(**record))
        db.commit()
        return {"status": "stored", "count": len(records)}
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()
```

```python
# celery_worker.py -- reset engine on worker fork
from celery.signals import worker_process_init
from app.db.session import sync_engine

@worker_process_init.connect
def reinit_db_engine(**kwargs):
    """Dispose the connection pool after fork so each child gets fresh connections."""
    sync_engine.dispose()
```

---

## 2. FastAPI File Upload (Large Files, Multiple, Background Processing)

### 2.1 Multiple Large File Upload with Streaming and Validation

```python
# app/api/uploads.py
import os
import uuid
import hashlib
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    BackgroundTasks,
    Depends,
    status,
)
from pydantic import BaseModel

router = APIRouter()

# --- Configuration ---
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
UPLOAD_DIR = Path("/data/uploads")
ALLOWED_CONTENT_TYPES = {
    "text/csv",
    "application/json",
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
CHUNK_SIZE = 1024 * 1024  # 1 MB


# --- Magic number validation ---
MAGIC_NUMBERS = {
    b"\x89PNG": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"%PDF": "application/pdf",
    b"PK": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


async def validate_file_magic(file: UploadFile) -> None:
    """Validate file content by reading the first bytes (magic number check)."""
    header = await file.read(8)
    await file.seek(0)  # Reset read position

    if file.content_type in ("text/csv", "application/json"):
        return  # Text formats don't have magic numbers

    for magic, expected_type in MAGIC_NUMBERS.items():
        if header.startswith(magic):
            if file.content_type != expected_type:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"File content does not match declared type: {file.content_type}",
                )
            return

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=f"Unrecognized file format",
    )


class UploadResult(BaseModel):
    filename: str
    saved_as: str
    size_bytes: int
    sha256: str
    status: str


@router.post("/upload", response_model=list[UploadResult])
async def upload_files(
    files: list[UploadFile] = File(..., description="Up to 10 files, 50MB each"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Upload multiple files with streaming writes and per-file validation.

    Files are written to disk in 1MB chunks to keep memory usage constant
    regardless of file size.
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files per request",
        )

    results: list[UploadResult] = []
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for file in files:
        # 1. Validate content type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {file.content_type} for {file.filename}",
            )

        # 2. Validate magic bytes
        await validate_file_magic(file)

        # 3. Generate safe filename
        ext = Path(file.filename).suffix.lower() if file.filename else ""
        safe_name = f"{uuid.uuid4().hex}{ext}"
        dest = UPLOAD_DIR / safe_name

        # 4. Stream file to disk in chunks, enforcing size limit
        sha256 = hashlib.sha256()
        total_bytes = 0

        async with aiofiles.open(dest, "wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE:
                    await out.close()
                    os.unlink(dest)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File {file.filename} exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit",
                    )
                sha256.update(chunk)
                await out.write(chunk)

        results.append(
            UploadResult(
                filename=file.filename or "unknown",
                saved_as=safe_name,
                size_bytes=total_bytes,
                sha256=sha256.hexdigest(),
                status="uploaded",
            )
        )

        # 5. Queue background processing (or use Celery for heavier work)
        background_tasks.add_task(_process_file_background, str(dest), safe_name)

    return results


async def _process_file_background(file_path: str, file_id: str) -> None:
    """Lightweight background processing. For heavy work, use Celery instead."""
    import logging
    logger = logging.getLogger("uploads")
    logger.info("Background processing started for %s", file_id)
    # ... parse, transform, store metadata, etc.
```

### 2.2 Configuring Starlette/Uvicorn for Large Uploads

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI()

# For files > 1MB, Starlette spools UploadFile to a temp file on disk automatically.
# The spool threshold is controlled at the Starlette level (default: 1MB).
# For very large bodies, you may need to configure the ASGI server:

# --- uvicorn CLI ---
# uvicorn app.main:app --limit-max-request-size 104857600  # 100 MB

# --- or in code ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        # Allow request bodies up to 100 MB
        limit_max_request_size=100 * 1024 * 1024,
    )
```

### 2.3 Submitting Uploaded Files to Celery

```python
# Combine upload endpoint with Celery task submission
from app.tasks.file_tasks import process_uploaded_file

@router.post("/upload-and-process")
async def upload_and_process(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a file, save to disk, then submit a Celery task for processing."""
    # ... stream file to disk (as above) ...
    dest = UPLOAD_DIR / safe_name

    # Submit to Celery
    task = process_uploaded_file.delay(str(dest), current_user.id)

    return {
        "file_id": safe_name,
        "task_id": task.id,
        "status": "processing",
        "poll_url": f"/api/tasks/{task.id}",
    }
```

---

## 3. FastAPI JWT Authentication (Cookie-Based)

### 3.1 Why Cookies Instead of Bearer Tokens

- **httpOnly** cookies cannot be read by JavaScript, mitigating XSS token theft.
- **SameSite=Strict** (or Lax) prevents the browser from sending the cookie on cross-site requests, reducing CSRF surface.
- **Secure** flag ensures the cookie is only sent over HTTPS.
- Trade-off: you now need CSRF protection (the "double-submit cookie" pattern).

### 3.2 Token Creation and Cookie Setting

```python
# app/auth/tokens.py
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt  # PyJWT -- actively maintained, preferred over python-jose
from pydantic import BaseModel
from app.config import settings


class TokenPayload(BaseModel):
    sub: int           # user ID
    exp: datetime
    iat: datetime
    jti: str           # unique token ID for revocation
    type: str          # "access" or "refresh"


def create_access_token(user_id: int, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),  # e.g. 15
        "iat": now,
        "jti": _generate_jti(),
        "type": "access",
        **(extra_claims or {}),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),  # e.g. 7
        "iat": now,
        "jti": _generate_jti(),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["sub", "exp", "iat", "jti", "type"]},
    )


def _generate_jti() -> str:
    import uuid
    return uuid.uuid4().hex
```

### 3.3 Login Endpoint -- Setting httpOnly Cookies

```python
# app/api/auth.py
import secrets
from fastapi import APIRouter, Response, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.tokens import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Cookie names
ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
CSRF_COOKIE = "csrf_token"         # readable by JS
CSRF_HEADER = "X-CSRF-Token"       # JS sends this header


@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    csrf_token = secrets.token_urlsafe(32)

    # Set access token -- httpOnly, not readable by JS
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        secure=True,              # HTTPS only in production
        samesite="strict",        # Strict prevents all cross-site sending
        max_age=60 * 15,          # 15 minutes
        path="/",
    )

    # Set refresh token -- httpOnly, restricted path
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/auth/refresh",       # Only sent to the refresh endpoint
    )

    # Set CSRF token -- NOT httpOnly so JS can read it
    response.set_cookie(
        key=CSRF_COOKIE,
        value=csrf_token,
        httponly=False,            # JS must read this to include in headers
        secure=True,
        samesite="strict",
        max_age=60 * 15,
        path="/",
    )

    return {"message": "Login successful"}
```

### 3.4 CSRF Protection -- Double-Submit Cookie Pattern

```python
# app/auth/csrf.py
from fastapi import Request, HTTPException, status


async def verify_csrf(request: Request) -> None:
    """
    Double-submit cookie pattern:
    1. Server sets a csrf_token cookie (readable by JS).
    2. Client JS reads the cookie and sends it as X-CSRF-Token header.
    3. Server verifies cookie value == header value.

    Why this works: an attacker on another origin cannot read cookies
    from your domain (Same-Origin Policy), so they cannot forge the header.
    """
    # Skip CSRF for safe methods
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    cookie_csrf = request.cookies.get("csrf_token")
    header_csrf = request.headers.get("X-CSRF-Token")

    if not cookie_csrf or not header_csrf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing",
        )

    if cookie_csrf != header_csrf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch",
        )
```

### 3.5 Auth Dependency (Preferred Over Middleware)

```python
# app/auth/dependencies.py
"""
Dependency injection is preferred over middleware for authentication because:
- It is opt-in per route (explicit > implicit).
- It provides better error messages and type safety.
- It integrates with FastAPI's dependency injection and OpenAPI docs.
- Middleware runs on every request including health checks and static files.
"""
from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from app.auth.tokens import decode_token
from app.auth.csrf import verify_csrf
from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
import jwt


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> "User":
    """Extract user from the httpOnly access_token cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user = await _get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# Reusable annotated dependency
CurrentUser = Annotated["User", Depends(get_current_user)]


# --- Combining CSRF + Auth for state-changing routes ---
async def get_authenticated_user_with_csrf(
    request: Request,
    _csrf: None = Depends(verify_csrf),
    user: "User" = Depends(get_current_user),
) -> "User":
    """Use this dependency on POST/PUT/DELETE routes that need CSRF protection."""
    return user


AuthenticatedUser = Annotated["User", Depends(get_authenticated_user_with_csrf)]
```

### 3.6 Usage in Routes

```python
# app/api/items.py
from fastapi import APIRouter
from app.auth.dependencies import CurrentUser, AuthenticatedUser

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
async def list_items(user: CurrentUser):
    """GET is safe -- no CSRF check needed, just auth."""
    return await _get_items_for_user(user.id)


@router.post("/")
async def create_item(data: ItemCreate, user: AuthenticatedUser):
    """POST requires both auth AND CSRF validation."""
    return await _create_item(user.id, data)
```

### 3.7 Token Refresh Endpoint

```python
@router.post("/auth/refresh")
async def refresh_tokens(request: Request, response: Response):
    """
    Rotate the refresh token on each use (refresh token rotation).
    The old refresh token is invalidated.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = decode_token(refresh_token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    # Check if this jti has been revoked (token rotation)
    if await _is_token_revoked(payload["jti"]):
        # Possible token theft -- revoke all tokens for this user
        await _revoke_all_tokens_for_user(payload["sub"])
        raise HTTPException(status_code=401, detail="Token reuse detected")

    # Revoke the old refresh token
    await _revoke_token(payload["jti"])

    # Issue new tokens
    new_access = create_access_token(payload["sub"])
    new_refresh = create_refresh_token(payload["sub"])
    new_csrf = secrets.token_urlsafe(32)

    # Set new cookies (same pattern as login)
    response.set_cookie(key="access_token", value=new_access, httponly=True, secure=True, samesite="strict", max_age=60*15, path="/")
    response.set_cookie(key="refresh_token", value=new_refresh, httponly=True, secure=True, samesite="strict", max_age=60*60*24*7, path="/auth/refresh")
    response.set_cookie(key="csrf_token", value=new_csrf, httponly=False, secure=True, samesite="strict", max_age=60*15, path="/")

    return {"message": "Tokens refreshed"}
```

### 3.8 Logout Endpoint

```python
@router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Clear all auth cookies and revoke tokens."""
    access_token = request.cookies.get("access_token")
    if access_token:
        try:
            payload = decode_token(access_token)
            await _revoke_token(payload["jti"])
        except jwt.InvalidTokenError:
            pass  # Token already invalid

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth/refresh")
    response.delete_cookie("csrf_token", path="/")
    return {"message": "Logged out"}
```

---

## 4. SQLAlchemy 2.0 + FastAPI

### 4.1 Async Engine and Session Setup

```python
# app/db/base.py
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 declarative base with naming conventions for Alembic.

    Naming conventions ensure Alembic autogenerate produces deterministic
    constraint names, which is critical for reliable migrations.
    """

    metadata_naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    # Apply naming convention to metadata
    metadata = Base.metadata
    metadata.naming_convention = metadata_naming_convention  # type: ignore[assignment]
```

**Note:** The naming convention above should be defined directly in the metadata constructor. Here is the corrected version:

```python
# app/db/base.py
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

### 4.2 Async Session Dependency (Production Pattern)

```python
# app/db/session.py
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,          # True only in development
    pool_size=20,                     # Max persistent connections
    max_overflow=10,                  # Extra connections under load
    pool_pre_ping=True,               # Verify connections before use
    pool_recycle=300,                 # Recycle connections after 5 minutes
    connect_args={
        "server_settings": {
            "jit": "off",             # Disable JIT for short queries (PostgreSQL)
        }
    },
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,           # Avoid lazy-load errors after commit
    autocommit=False,
    autoflush=False,                  # Flush explicitly for predictability
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields one async session per request.

    The session is committed on success and rolled back on exception.
    FastAPI's dependency system caches this within a single request,
    so multiple Depends(get_db) calls return the SAME session.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Reusable type alias
DbSession = Annotated[AsyncSession, Depends(get_db)]
```

### 4.3 Model Definitions (SQLAlchemy 2.0 Style)

```python
# app/models/user.py
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    items: Mapped[list["Item"]] = relationship(back_populates="owner", lazy="selectin")
```

### 4.4 CRUD Operations with Async Session

```python
# app/crud/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.flush()    # Generate the ID without committing
    await db.refresh(user)
    return user
    # Commit happens in the get_db dependency on successful return
```

### 4.5 Route Usage

```python
# app/api/users.py
from fastapi import APIRouter
from app.db.session import DbSession
from app.crud import user as user_crud

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(user_id: int, db: DbSession):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404)
    return user
```

### 4.6 Alembic Setup for Async SQLAlchemy

```bash
# Initialize Alembic with the async template
alembic init -t async migrations
```

```python
# migrations/env.py
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import your Base and all models so Alembic sees them
from app.db.base import Base
from app.models import user, item  # noqa: F401 -- import for side effects
from app.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode -- generates SQL without connecting."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Compare types and server defaults for more accurate autogenerate
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with an async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't pool connections during migrations
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4.7 Alembic Best Practices

```ini
# alembic.ini -- key settings
[alembic]
script_location = migrations
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(rev)s_%%(slug)s
# ^ Produces: 2026_02_13_abc123_add_users_table.py (sortable by date)
```

```bash
# Generate a migration
alembic revision --autogenerate -m "add users table"

# Review the generated migration before applying!
# Never blindly trust autogenerate.

# Apply migrations
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history --verbose
```

**Alembic migration tips:**
- Always review autogenerated migrations. Alembic cannot detect: table renames (it sees drop+create), column renames, or changes to CHECK constraints.
- For data migrations (backfilling), use `op.get_bind()` and run SQL directly:

```python
# Inside a migration upgrade() function
def upgrade() -> None:
    # Schema change
    op.add_column("users", sa.Column("display_name", sa.String(255)))

    # Data migration -- use the connection directly
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE users SET display_name = full_name WHERE display_name IS NULL")
    )
```

---

## 5. Azure Blob Storage with Python

### 5.1 Client Setup with Retry Policy

```python
# app/storage/azure_blob.py
from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    generate_blob_sas,
    BlobSasPermissions,
)
from azure.storage.blob._retry import ExponentialRetry
from app.config import settings


def get_blob_service_client() -> BlobServiceClient:
    """
    Create a BlobServiceClient with tuned retry and performance settings.

    Best practice: Use DefaultAzureCredential (Managed Identity in production,
    developer credentials locally) instead of connection strings.
    """
    credential = DefaultAzureCredential()

    # Custom retry policy
    retry_policy = ExponentialRetry(
        initial_backoff=1,       # 1 second initial backoff
        increment_base=2,        # Exponential base (1s, 2s, 4s, 8s ...)
        retry_total=5,           # Total retry attempts
        retry_to_secondary=True, # Retry to RA-GRS secondary endpoint
    )

    client = BlobServiceClient(
        account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=credential,

        # Retry configuration
        retry_policy=retry_policy,

        # Performance tuning
        max_single_put_size=64 * 1024 * 1024,   # 64 MB -- upload in one PUT if smaller
        max_block_size=4 * 1024 * 1024,          # 4 MB blocks for chunked uploads
        max_page_size=4 * 1024 * 1024,

        # Connection settings
        connection_timeout=20,
        read_timeout=120,
    )
    return client


# Module-level singleton (reuse across requests)
_blob_client: BlobServiceClient | None = None


def get_blob_client() -> BlobServiceClient:
    global _blob_client
    if _blob_client is None:
        _blob_client = get_blob_service_client()
    return _blob_client
```

### 5.2 Upload and Download Patterns

```python
# app/storage/operations.py
import io
from pathlib import Path

from azure.storage.blob import ContentSettings
from app.storage.azure_blob import get_blob_client
from app.config import settings


def upload_blob_from_file(
    container_name: str,
    blob_name: str,
    file_path: str | Path,
    content_type: str = "application/octet-stream",
) -> str:
    """Upload a file to Azure Blob Storage. Returns the blob URL."""
    client = get_blob_client()
    blob = client.get_blob_client(container=container_name, blob=blob_name)

    content_settings = ContentSettings(content_type=content_type)

    with open(file_path, "rb") as data:
        blob.upload_blob(
            data,
            overwrite=True,
            content_settings=content_settings,
            max_concurrency=4,          # Parallel block uploads
            timeout=300,                 # 5 minute timeout
        )

    return blob.url


def upload_blob_from_bytes(
    container_name: str,
    blob_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """Upload raw bytes to Azure Blob Storage."""
    client = get_blob_client()
    blob = client.get_blob_client(container=container_name, blob=blob_name)

    blob.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )
    return blob.url


def download_blob_to_bytes(container_name: str, blob_name: str) -> bytes:
    """Download a blob and return its contents as bytes."""
    client = get_blob_client()
    blob = client.get_blob_client(container=container_name, blob=blob_name)

    stream = blob.download_blob(max_concurrency=4)
    return stream.readall()


def download_blob_to_file(container_name: str, blob_name: str, dest_path: str | Path) -> None:
    """Download a blob directly to a file on disk (memory-efficient for large blobs)."""
    client = get_blob_client()
    blob = client.get_blob_client(container=container_name, blob=blob_name)

    with open(dest_path, "wb") as f:
        stream = blob.download_blob(max_concurrency=4)
        stream.readinto(f)


def download_blob_stream(container_name: str, blob_name: str):
    """Return a streaming download for very large blobs."""
    client = get_blob_client()
    blob = client.get_blob_client(container=container_name, blob=blob_name)
    return blob.download_blob(max_concurrency=4)
```

### 5.3 Async Blob Operations

```python
# app/storage/async_operations.py
"""
Async Azure Blob Storage operations.

Requires: pip install azure-storage-blob aiohttp
The async API uses aiohttp as the transport.
"""
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
from azure.storage.blob import ContentSettings
from app.config import settings


async def get_async_blob_client() -> AsyncBlobServiceClient:
    credential = AsyncDefaultAzureCredential()
    return AsyncBlobServiceClient(
        account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=credential,
        max_single_put_size=64 * 1024 * 1024,
        max_block_size=4 * 1024 * 1024,
        connection_timeout=20,
        read_timeout=120,
    )


async def async_upload_blob(
    container_name: str,
    blob_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    async with await get_async_blob_client() as client:
        blob = client.get_blob_client(container=container_name, blob=blob_name)
        await blob.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob.url


async def async_download_blob(container_name: str, blob_name: str) -> bytes:
    async with await get_async_blob_client() as client:
        blob = client.get_blob_client(container=container_name, blob=blob_name)
        stream = await blob.download_blob()
        return await stream.readall()
```

### 5.4 SAS Token Generation

```python
# app/storage/sas.py
"""
SAS token generation patterns.

Hierarchy of preference (most to least secure):
1. User Delegation SAS (uses Entra ID / AAD credentials) -- RECOMMENDED
2. Service SAS (uses storage account key)
3. Account SAS (uses storage account key, broader scope)

Never use connection strings with embedded account keys in production.
"""
from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobServiceClient,
    generate_blob_sas,
    BlobSasPermissions,
    UserDelegationKey,
)
from app.config import settings


def get_user_delegation_key() -> tuple[BlobServiceClient, UserDelegationKey]:
    """Get a user delegation key valid for 7 days."""
    credential = DefaultAzureCredential()
    client = BlobServiceClient(
        account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=credential,
    )
    start = datetime.now(timezone.utc)
    expiry = start + timedelta(days=7)
    key = client.get_user_delegation_key(start, expiry)
    return client, key


def generate_read_sas(
    container_name: str,
    blob_name: str,
    expiry_hours: int = 1,
) -> str:
    """
    Generate a read-only SAS URL for a blob.

    Use User Delegation SAS (preferred) which does not require
    the storage account key.
    """
    _, delegation_key = get_user_delegation_key()

    sas_token = generate_blob_sas(
        account_name=settings.AZURE_STORAGE_ACCOUNT,
        container_name=container_name,
        blob_name=blob_name,
        user_delegation_key=delegation_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
        start=datetime.now(timezone.utc) - timedelta(minutes=5),  # Clock skew tolerance
    )

    return (
        f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"
        f"/{container_name}/{blob_name}?{sas_token}"
    )


def generate_upload_sas(
    container_name: str,
    blob_name: str,
    expiry_minutes: int = 30,
) -> str:
    """Generate a write SAS URL for client-side direct uploads."""
    _, delegation_key = get_user_delegation_key()

    sas_token = generate_blob_sas(
        account_name=settings.AZURE_STORAGE_ACCOUNT,
        container_name=container_name,
        blob_name=blob_name,
        user_delegation_key=delegation_key,
        permission=BlobSasPermissions(write=True, create=True),
        expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
        start=datetime.now(timezone.utc) - timedelta(minutes=5),
    )

    return (
        f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"
        f"/{container_name}/{blob_name}?{sas_token}"
    )
```

### 5.5 FastAPI Integration

```python
# app/api/files.py
from fastapi import APIRouter, UploadFile, File
from app.storage.operations import upload_blob_from_bytes
from app.storage.sas import generate_read_sas

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to Azure Blob Storage and return a SAS URL."""
    content = await file.read()
    blob_name = f"uploads/{file.filename}"

    upload_blob_from_bytes(
        container_name="user-files",
        blob_name=blob_name,
        data=content,
        content_type=file.content_type or "application/octet-stream",
    )

    sas_url = generate_read_sas("user-files", blob_name, expiry_hours=24)
    return {"blob_name": blob_name, "download_url": sas_url}
```

---

## Configuration Template

```python
# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/mydb"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://user:pass@localhost:5432/mydb"
    SQL_ECHO: bool = False

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # JWT
    JWT_SECRET_KEY: str  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Azure
    AZURE_STORAGE_ACCOUNT: str = ""

    # File uploads
    UPLOAD_DIR: str = "/data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

---

## Requirements

```
# requirements.txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic-settings>=2.0
sqlalchemy[asyncio]>=2.0.30
asyncpg>=0.29.0
psycopg2-binary>=2.9.9
alembic>=1.13.0
celery[redis]>=5.4.0
redis>=5.0
PyJWT>=2.8.0
passlib[bcrypt]>=1.7.4
aiofiles>=23.2.0
azure-storage-blob>=12.20.0
azure-identity>=1.16.0
aiohttp>=3.9.0
python-multipart>=0.0.9
```

---

## Sources

### FastAPI + Celery
- [FastAPI + Celery Production Guide 2025](https://medium.com/@dewasheesh.rana/celery-redis-fastapi-the-ultimate-2025-production-guide-broker-vs-backend-explained-5b84ef508fa7)
- [Complete Guide to Background Processing with FastAPI x Celery](https://blog.greeden.me/en/2026/01/27/the-complete-guide-to-background-processing-with-fastapi-x-celery-redishow-to-separate-heavy-work-from-your-api-to-keep-services-stable/)
- [FastAPI + Celery: Idempotent Tasks and Retries](https://medium.com/@hjparmar1944/fastapi-celery-work-queues-idempotent-tasks-and-retries-that-dont-duplicate-d05e820c904b)
- [Celery Tasks Guide](https://docs.celeryq.dev/en/stable/userguide/tasks.html)
- [SQLAlchemy Session Handling in Celery Tasks](https://celery.school/sqlalchemy-session-celery-tasks)
- [FastAPI Best Practices for Production 2026](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026)

### File Uploads
- [FastAPI Request Files Documentation](https://fastapi.tiangolo.com/tutorial/request-files/)
- [Uploading Files Using FastAPI (Better Stack)](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/)
- [Multi-Part File Uploads and Validation in FastAPI](https://medium.com/@bhagyarana80/multi-part-file-uploads-and-validation-in-fastapi-for-large-datasets-9a3a71f0c475)
- [Async File Uploads in FastAPI](https://medium.com/@connect.hashblock/async-file-uploads-in-fastapi-handling-gigabyte-scale-data-smoothly-aec421335680)

### JWT Authentication
- [Security Design with FastAPI: JWT, CSRF, Cookie Sessions](https://blog.greeden.me/en/2025/10/14/a-beginners-guide-to-serious-security-design-with-fastapi-authentication-authorization-jwt-oauth2-cookie-sessions-rbac-scopes-csrf-protection-and-real-world-pitfalls/)
- [FastAPI JWT httpOnly Cookie Tutorial](https://www.fastapitutorial.com/blog/fastapi-jwt-httponly-cookie/)
- [FastAPI Cookie-based JWT Tokens Discussion](https://github.com/fastapi/fastapi/discussions/9142)
- [FastAPI CSRF Protection (StackHawk)](https://www.stackhawk.com/blog/csrf-protection-in-fastapi/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)

### SQLAlchemy 2.0 + Alembic
- [Patterns and Practices for SQLAlchemy 2.0 with FastAPI](https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy)
- [Setting up FastAPI with Async SQLAlchemy 2.0](https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308)
- [SQLAlchemy Async I/O Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Async Template](https://github.com/sqlalchemy/alembic/blob/main/alembic/templates/async/env.py)
- [Database Session Management Best Architecture](https://deepwiki.com/fastapi-practices/fastapi_best_architecture/7.6-database-session-management)

### Azure Blob Storage
- [Azure Storage Blobs Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme)
- [Retry Policy for Azure Blob Storage (Python)](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-retry-policy-python)
- [User Delegation SAS with Python](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-python)
- [Performance Tuning for Azure Blob Python SDK](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-tune-upload-download-python)
- [Upload a Blob with Python](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-upload-python)
