"""FastAPI dependencies for authentication and authorization."""

import logging

import jwt
import redis
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from api.db.models import User
from api.db.session import get_db
from api.services.auth_service import decode_access_token
from api.services.data_service import DataStore
from api.settings import settings

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    """Lazy-initialize Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Extract JWT from Bearer header or httpOnly cookie, validate, return user."""
    # Try Bearer header first (agent-friendly), then cookie (browser-friendly)
    token = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account deactivated",
        )
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require the current user to have admin role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def get_active_cycle_year(request: Request) -> int:
    """Derive active cycle year from loaded data."""
    store: DataStore = request.app.state.store
    if store.master_data.empty:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No data loaded",
        )
    return int(store.master_data["app_year"].max())


def rate_limit(key_prefix: str, max_requests: int, window_seconds: int):
    """Create a rate-limiting dependency backed by Redis.

    Falls back to no rate limiting if Redis is unavailable.
    """
    def dependency(current_user: User = Depends(get_current_user)):
        try:
            r = _get_redis()
            key = f"rate:{key_prefix}:{current_user.id}"
            current = r.incr(key)
            if current == 1:
                r.expire(key, window_seconds)
            if current > max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )
        except redis.ConnectionError:
            logger.warning("Redis unavailable for rate limiting, skipping")
        return current_user
    return dependency
