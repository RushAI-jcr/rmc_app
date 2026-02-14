"""FastAPI application for Rush Medical College Admissions Triage."""

import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on the Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.services.data_service import DataStore
from api.routers import applicants, triage, review, fairness, stats
from api.routers import auth, ingest
from api.routers import pipeline as pipeline_router
from api.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load data and models at startup."""
    # Validate security configuration
    if settings.environment not in ("development", "test"):
        if len(settings.jwt_secret) < 32:
            raise RuntimeError("JWT_SECRET must be at least 32 characters in production")
        if "localhost" in settings.database_url or "postgres:postgres" in settings.database_url:
            raise RuntimeError("DATABASE_URL must not use default credentials in production")

    logger.info("Loading data and models...")
    store = DataStore()
    store.load_all()
    app.state.store = store
    logger.info("API ready. Master data: %d rows, Models: %s",
                len(store.master_data), list(store.model_results.keys()))
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="RMC Admissions Triage API",
    description="Decision-support tool for Rush Medical College admissions review",
    version="1.0.0",
    lifespan=lifespan,
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],  # Restrict to only methods actually used
    allow_headers=["Content-Type", "Authorization"],  # Restrict headers
)

app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(pipeline_router.router)
app.include_router(applicants.router)
app.include_router(triage.router)
app.include_router(review.router)
app.include_router(fairness.router)
app.include_router(stats.router)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}
