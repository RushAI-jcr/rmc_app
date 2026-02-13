"""FastAPI dependencies for authentication."""

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from api.db.models import User
from api.db.session import get_db
from api.services.auth_service import decode_access_token


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
    return user
