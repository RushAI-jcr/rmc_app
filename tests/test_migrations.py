"""Structural validation for Alembic migrations.

These tests verify migration integrity without requiring a running database.
"""
import ast
import re
from pathlib import Path

import pytest

ALEMBIC_INI = Path("api/alembic.ini")
VERSIONS_DIR = Path("api/alembic/versions")


class TestMigrationStructure:
    def test_alembic_ini_exists_and_parseable(self):
        assert ALEMBIC_INI.exists(), "api/alembic.ini not found"
        content = ALEMBIC_INI.read_text()
        assert "script_location" in content
        assert "api/alembic" in content

    def test_migration_versions_directory_exists(self):
        assert VERSIONS_DIR.exists(), "api/alembic/versions/ not found"

    def test_at_least_one_migration_exists(self):
        scripts = list(VERSIONS_DIR.glob("*.py"))
        scripts = [s for s in scripts if s.name != "__pycache__"]
        assert len(scripts) >= 1, "No migration scripts found"

    def test_all_migrations_have_revision_and_down_revision(self):
        """Every migration must declare revision and down_revision."""
        for script in VERSIONS_DIR.glob("*.py"):
            if script.name.startswith("__"):
                continue
            content = script.read_text()
            assert re.search(r'^revision\s*[=:]', content, re.MULTILINE), (
                f"{script.name} missing 'revision' variable"
            )
            assert re.search(r'^down_revision\s*[=:]', content, re.MULTILINE), (
                f"{script.name} missing 'down_revision' variable"
            )

    def test_all_migrations_have_upgrade_and_downgrade(self):
        """Every migration must define upgrade() and downgrade()."""
        for script in VERSIONS_DIR.glob("*.py"):
            if script.name.startswith("__"):
                continue
            content = script.read_text()
            assert "def upgrade()" in content, (
                f"{script.name} missing upgrade() function"
            )
            assert "def downgrade()" in content, (
                f"{script.name} missing downgrade() function"
            )

    def test_revision_chain_is_linear(self):
        """Verify no orphan revisions — each down_revision points to a known revision or None."""
        revisions = {}
        for script in VERSIONS_DIR.glob("*.py"):
            if script.name.startswith("__"):
                continue
            content = script.read_text()

            # Handles both `revision = "x"` and `revision: str = "x"`
            rev_match = re.search(r'^revision(?:\s*:\s*str)?\s*=\s*["\'](.+?)["\']', content, re.MULTILINE)
            down_match = re.search(r'^down_revision(?:\s*:\s*[^=]+)?\s*=\s*(.+)', content, re.MULTILINE)

            assert rev_match, f"{script.name}: could not parse revision"
            rev_id = rev_match.group(1)

            if down_match:
                raw = down_match.group(1).strip()
                # Extract quoted string or detect None
                quoted = re.search(r'["\'](.+?)["\']', raw)
                if quoted:
                    down_id = quoted.group(1)
                else:
                    down_id = None
            else:
                down_id = None

            revisions[rev_id] = {"file": script.name, "down_revision": down_id}

        # Verify chain integrity
        assert len(revisions) >= 1, "No revisions found"

        roots = [r for r, info in revisions.items() if info["down_revision"] is None]
        assert len(roots) == 1, (
            f"Expected exactly 1 root migration (down_revision=None), found {len(roots)}: {roots}"
        )

        # Every non-root down_revision must point to an existing revision
        for rev_id, info in revisions.items():
            if info["down_revision"] is not None:
                assert info["down_revision"] in revisions, (
                    f"{info['file']}: down_revision '{info['down_revision']}' "
                    f"does not match any known revision"
                )

    def test_migrations_are_syntactically_valid(self):
        """All migration files must be valid Python."""
        for script in VERSIONS_DIR.glob("*.py"):
            if script.name.startswith("__"):
                continue
            content = script.read_text()
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"{script.name} has syntax error: {e}")
