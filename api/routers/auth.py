"""Authentication endpoints: login, logout, current user."""

import time
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.db.models import User
from api.db.session import get_db
from api.dependencies import get_current_user
from api.services.auth_service import create_access_token, verify_password
from api.services.audit_service import log_action
from api.settings import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simple in-memory rate limiter for login endpoint
_login_attempts: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 5  # max attempts
_RATE_WINDOW = 60  # per 60 seconds


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: str
    username: str
    role: str


@router.post("/login")
def login(body: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    # Rate limit by client IP
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    attempts = _login_attempts[client_ip]
    # Prune expired entries
    _login_attempts[client_ip] = [t for t in attempts if now - t < _RATE_WINDOW]
    if len(_login_attempts[client_ip]) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )
    _login_attempts[client_ip].append(now)

    user = db.query(User).filter(User.username == body.username).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(user.id, user.username)
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="strict",
        secure=settings.environment != "development",
        max_age=settings.jwt_expiration_minutes * 60,
        path="/",
    )

    log_action(db, user.id, "login")
    return {"status": "ok", "username": user.username}


@router.post("/logout")
def logout(response: Response, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    response.delete_cookie("access_token", path="/")
    log_action(db, user.id, "logout")
    return {"status": "ok"}


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> UserInfo:
    return UserInfo(id=str(user.id), username=user.username, role=user.role)
