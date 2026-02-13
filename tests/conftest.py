"""Shared fixtures for the RMC test suite."""

import os
import uuid

import pytest

# Set test environment variables BEFORE importing any app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///")
os.environ.setdefault("JWT_SECRET", "test-secret-key-must-be-at-least-32-characters-long")
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture()
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture()
def other_user_id() -> uuid.UUID:
    return uuid.uuid4()
