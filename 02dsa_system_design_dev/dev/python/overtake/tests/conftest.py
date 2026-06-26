"""Shared pytest fixtures.

Everything runs offline: SQLite in-memory DB, the in-memory vector store, and
the EchoProvider. The S3-backed storage dependency is overridden with a fake so
no AWS/LocalStack is needed.
"""

from __future__ import annotations

import os

# Force fully-offline config BEFORE app import. OS env vars take precedence over
# the real ``.env`` file in pydantic-settings, so this guarantees an in-memory
# SQLite DB and no AWS/LocalStack contact regardless of what ``.env`` contains.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.main as app_main
from app.api.deps import storage_dep
from app.ai.rag.vector_store import get_vector_store
from app.core.config import get_settings
from app.infra.db import set_engine
from app.main import app

get_settings.cache_clear()


class FakeStorage:
    """In-memory object store standing in for S3 during tests."""

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}

    def ensure_bucket(self) -> None:  # pragma: no cover - noop
        pass

    def put(self, key: str, body: bytes, content_type: str) -> None:
        self._objects[key] = body

    def get(self, key: str) -> bytes:
        return self._objects[key]

    def delete(self, key: str) -> None:
        self._objects.pop(key, None)


# The lifespan calls get_storage() DIRECTLY (not via the FastAPI dependency), so
# patch the name in app.main to avoid any real S3/boto connection (and its multi-
# second connect timeout) during the test run.
setattr(app_main, "get_storage", lambda settings=None: FakeStorage())


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(eng)
    set_engine(eng)
    yield eng
    SQLModel.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture(autouse=True)
def clean_vector_store():
    get_vector_store().clear()
    yield
    get_vector_store().clear()


@pytest.fixture
def client(engine):
    """TestClient with the engine set and S3 storage faked out.

    A SINGLE FakeStorage instance is shared across all requests in the test so
    an upload and a later download see the same in-memory objects.
    """
    fake_storage = FakeStorage()
    app.dependency_overrides[storage_dep] = lambda: fake_storage
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, username: str = "alice") -> str:
    """Helper: register a user and return a bearer token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "password123",
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "password123"},
    )
    return resp.json()["access_token"]
