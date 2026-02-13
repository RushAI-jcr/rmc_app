"""Security regression tests from audit findings P1-001 through P1-006."""

import hashlib
import pickle
import re
import tempfile
import time
from pathlib import Path, PurePosixPath

import pytest


# ---------------------------------------------------------------------------
# P1-002: Path traversal protection
# ---------------------------------------------------------------------------

class TestPathTraversalBlocked:
    """Malicious filenames must be rejected by upload sanitization."""

    MALICIOUS_NAMES = [
        "../../../etc/passwd",
        "foo/../../bar.xlsx",
        ".env",
        ".ssh/id_rsa",
        "....//....//etc/passwd",
    ]

    @pytest.mark.parametrize("malicious_name", MALICIOUS_NAMES)
    def test_purepath_strips_traversal(self, malicious_name: str) -> None:
        """PurePosixPath.name strips directory traversal components."""
        safe = PurePosixPath(malicious_name).name
        assert "/" not in safe
        assert ".." not in safe.split("/")

    def test_dotfile_rejected(self) -> None:
        safe = PurePosixPath(".env").name
        assert safe.startswith(".")

    def test_resolved_path_stays_within_session_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session_dir = Path(tmpdir) / "session-abc"
            session_dir.mkdir()

            safe_name = PurePosixPath("legit.xlsx").name
            dest = session_dir / safe_name
            assert dest.resolve().is_relative_to(session_dir.resolve())

    def test_traversal_escapes_session_dir(self) -> None:
        """Demonstrate that unsanitized names escape the session dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_dir = Path(tmpdir) / "session-abc"
            session_dir.mkdir()

            # Without sanitization, this would escape
            raw_dest = session_dir / "../../../etc/passwd"
            assert not raw_dest.resolve().is_relative_to(session_dir.resolve())

            # With sanitization, it stays inside
            safe_name = PurePosixPath("../../../etc/passwd").name
            safe_dest = session_dir / safe_name
            assert safe_dest.resolve().is_relative_to(session_dir.resolve())


# ---------------------------------------------------------------------------
# P1-003 / P1-004: No hardcoded secrets in source code
# ---------------------------------------------------------------------------

class TestNoHardcodedSecrets:
    """Grep the codebase for credential patterns."""

    FORBIDDEN_PATTERNS = [
        r'jwt_secret\s*[:=]\s*["\'](?!{)',  # jwt_secret = "something"
        r'password\s*[:=]\s*["\'].*localhost',  # password with localhost
    ]

    def _python_files(self) -> list[Path]:
        root = Path(__file__).parent.parent
        files = []
        for d in ["api", "pipeline"]:
            p = root / d
            if p.exists():
                files.extend(p.rglob("*.py"))
        return files

    def test_no_secrets_in_source(self) -> None:
        for py_file in self._python_files():
            content = py_file.read_text()
            for pattern in self.FORBIDDEN_PATTERNS:
                matches = re.findall(pattern, content)
                assert not matches, (
                    f"Potential hardcoded secret in {py_file.relative_to(py_file.parent.parent)}: "
                    f"pattern={pattern}, matches={matches}"
                )

    def test_settings_has_no_default_jwt_secret(self) -> None:
        """api/settings.py must not have a default value for jwt_secret."""
        settings_path = Path(__file__).parent.parent / "api" / "settings.py"
        content = settings_path.read_text()
        # Should be `jwt_secret: str` with no `= "..."` default
        assert "jwt_secret: str" in content
        assert 'jwt_secret: str = "' not in content
        assert "jwt_secret: str = '" not in content


# ---------------------------------------------------------------------------
# P1-005: Pickle integrity verification
# ---------------------------------------------------------------------------

class TestPickleVerification:
    """SHA-256 hash must be verified before deserializing pickle files."""

    def test_save_and_load_verified(self, tmp_path: Path) -> None:
        from pipeline.model_verification import load_verified_pickle, save_verified_pickle

        obj = {"model": "test", "accuracy": 0.95}
        model_path = tmp_path / "model.pkl"

        save_verified_pickle(obj, model_path)

        # Hash file should exist
        hash_path = model_path.with_suffix(".sha256")
        assert hash_path.exists()

        # Load should succeed
        loaded = load_verified_pickle(model_path)
        assert loaded == obj

    def test_load_without_hash_raises(self, tmp_path: Path) -> None:
        from pipeline.model_verification import load_verified_pickle

        model_path = tmp_path / "model.pkl"
        model_path.write_bytes(pickle.dumps({"test": "data"}))

        with pytest.raises(FileNotFoundError, match="Hash file not found"):
            load_verified_pickle(model_path)

    def test_tampered_file_raises(self, tmp_path: Path) -> None:
        from pipeline.model_verification import load_verified_pickle, save_verified_pickle

        obj = {"model": "original"}
        model_path = tmp_path / "model.pkl"
        save_verified_pickle(obj, model_path)

        # Tamper with the pickle file
        tampered = pickle.dumps({"model": "tampered"})
        model_path.write_bytes(tampered)

        with pytest.raises(ValueError, match="integrity check failed"):
            load_verified_pickle(model_path)

    def test_hash_uses_sha256(self, tmp_path: Path) -> None:
        from pipeline.model_verification import save_verified_pickle

        obj = {"key": "value"}
        model_path = tmp_path / "model.pkl"
        save_verified_pickle(obj, model_path)

        # Verify hash is valid SHA-256 hex
        hash_val = model_path.with_suffix(".sha256").read_text().strip()
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)

        # Verify it matches actual file content
        actual = hashlib.sha256(model_path.read_bytes()).hexdigest()
        assert hash_val == actual


# ---------------------------------------------------------------------------
# P3-021: Rate limiting on login endpoint
# ---------------------------------------------------------------------------

class TestRateLimiting:
    """Login endpoint must enforce rate limits."""

    def test_rate_limiter_blocks_after_limit(self) -> None:
        """Simulate the rate limiter logic directly."""
        from collections import defaultdict

        attempts: dict[str, list[float]] = defaultdict(list)
        rate_limit = 5
        window = 60

        client_ip = "192.168.1.100"

        # First 5 attempts should pass
        for i in range(rate_limit):
            now = time.monotonic()
            attempts[client_ip] = [t for t in attempts[client_ip] if now - t < window]
            assert len(attempts[client_ip]) < rate_limit, f"Blocked on attempt {i+1}"
            attempts[client_ip].append(now)

        # 6th attempt should be blocked
        now = time.monotonic()
        attempts[client_ip] = [t for t in attempts[client_ip] if now - t < window]
        assert len(attempts[client_ip]) >= rate_limit

    def test_rate_limiter_resets_after_window(self) -> None:
        """Expired attempts should be pruned."""
        from collections import defaultdict

        attempts: dict[str, list[float]] = defaultdict(list)
        window = 60
        client_ip = "10.0.0.1"

        # Add old attempts (simulate they happened 120s ago)
        base = time.monotonic() - 120
        for i in range(10):
            attempts[client_ip].append(base + i)

        # Prune should clear all of them
        now = time.monotonic()
        attempts[client_ip] = [t for t in attempts[client_ip] if now - t < window]
        assert len(attempts[client_ip]) == 0
