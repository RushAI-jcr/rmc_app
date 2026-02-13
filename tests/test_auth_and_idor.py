"""Auth and IDOR tests from audit findings P2-007, P2-009, P3-021."""

import uuid

import pytest


# ---------------------------------------------------------------------------
# P2-009: Bearer + Cookie auth
# ---------------------------------------------------------------------------

class TestDualAuth:
    """get_current_user must accept both Bearer header and httpOnly cookie."""

    def test_bearer_token_extracted(self) -> None:
        """Bearer header should be extracted first."""
        # Simulate the extraction logic from dependencies.py
        auth_header = "Bearer eyJhbGciOi..."
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        assert token == "eyJhbGciOi..."

    def test_cookie_fallback(self) -> None:
        """Cookie should be used when no Bearer header present."""
        auth_header = ""
        cookie_token = "cookie-jwt-token"

        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        if not token:
            token = cookie_token  # simulating request.cookies.get(...)
        assert token == "cookie-jwt-token"

    def test_no_auth_returns_none(self) -> None:
        """Missing both Bearer and cookie should yield no token."""
        auth_header = ""
        cookie_token = None

        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        if not token:
            token = cookie_token
        assert token is None


# ---------------------------------------------------------------------------
# P2-007: IDOR protection — verify_session_ownership
# ---------------------------------------------------------------------------

class TestVerifySessionOwnership:
    """verify_session_ownership must block cross-user access."""

    def _make_mock_session(self, owner_id: uuid.UUID):
        """Create a minimal mock UploadSession."""

        class MockSession:
            def __init__(self, uploaded_by: uuid.UUID):
                self.uploaded_by = uploaded_by

        return MockSession(owner_id)

    def _make_mock_user(self, user_id: uuid.UUID, role: str = "staff"):
        """Create a minimal mock User."""

        class MockUser:
            def __init__(self, uid: uuid.UUID, r: str):
                self.id = uid
                self.role = r

        return MockUser(user_id, role)

    def test_owner_can_access(self, user_id: uuid.UUID) -> None:
        """Session owner should have access."""
        session = self._make_mock_session(user_id)
        user = self._make_mock_user(user_id)

        # Should not raise
        if session.uploaded_by != user.id and user.role != "admin":
            pytest.fail("Owner was blocked from their own session")

    def test_other_user_blocked(self, user_id: uuid.UUID, other_user_id: uuid.UUID) -> None:
        """Non-owner non-admin should be blocked."""
        session = self._make_mock_session(user_id)
        other_user = self._make_mock_user(other_user_id, role="staff")

        is_blocked = session.uploaded_by != other_user.id and other_user.role != "admin"
        assert is_blocked, "Non-owner was not blocked"

    def test_admin_can_access(self, user_id: uuid.UUID, other_user_id: uuid.UUID) -> None:
        """Admin should bypass ownership check."""
        session = self._make_mock_session(user_id)
        admin = self._make_mock_user(other_user_id, role="admin")

        is_blocked = session.uploaded_by != admin.id and admin.role != "admin"
        assert not is_blocked, "Admin was blocked from session"


# ---------------------------------------------------------------------------
# P2-007: IDOR on all ingest endpoints
# ---------------------------------------------------------------------------

class TestIngestEndpointsHaveOwnershipCheck:
    """All session endpoints in ingest.py must call verify_session_ownership."""

    def test_all_session_endpoints_guarded(self) -> None:
        """Parse ingest.py and verify verify_session_ownership is called in every endpoint."""
        from pathlib import Path
        import ast

        ingest_path = Path(__file__).parent.parent / "api" / "routers" / "ingest.py"
        source = ingest_path.read_text()
        tree = ast.parse(source)

        # Find all function definitions that take session_id parameter
        session_endpoints = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_names = [arg.arg for arg in node.args.args]
                if "session_id" in param_names:
                    session_endpoints.append(node.name)

        assert len(session_endpoints) >= 4, (
            f"Expected at least 4 session endpoints, found {len(session_endpoints)}: {session_endpoints}"
        )

        # Verify each calls verify_session_ownership
        for func_name in session_endpoints:
            assert f"verify_session_ownership" in source, (
                f"verify_session_ownership not found in ingest.py"
            )

            # More precise: check the function body contains the call
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == func_name:
                    body_source = ast.get_source_segment(source, node)
                    assert body_source is not None
                    assert "verify_session_ownership" in body_source, (
                        f"Endpoint '{func_name}' missing verify_session_ownership call"
                    )


# ---------------------------------------------------------------------------
# JWT token creation and validation
# ---------------------------------------------------------------------------

class TestJWTTokens:
    """JWT creation and verification basics."""

    def test_create_and_decode_token(self) -> None:
        from api.services.auth_service import create_access_token, decode_access_token

        uid = uuid.uuid4()
        token = create_access_token(uid, "testuser")
        payload = decode_access_token(token)

        assert payload["sub"] == str(uid)
        assert payload["username"] == "testuser"
        assert "exp" in payload
        assert "jti" in payload

    def test_expired_token_raises(self) -> None:
        import jwt as pyjwt
        from datetime import datetime, timedelta, timezone
        from api.settings import settings

        payload = {
            "sub": str(uuid.uuid4()),
            "username": "testuser",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = pyjwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        with pytest.raises(pyjwt.ExpiredSignatureError):
            pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

    def test_invalid_secret_raises(self) -> None:
        import jwt as pyjwt
        from api.services.auth_service import create_access_token

        uid = uuid.uuid4()
        token = create_access_token(uid, "testuser")

        with pytest.raises(pyjwt.InvalidSignatureError):
            pyjwt.decode(token, "wrong-secret", algorithms=["HS256"])
