"""Shared pytest fixtures.

Everything runs offline: SQLite in-memory DB, the in-memory vector store, and
the EchoProvider. The S3-backed storage dependency is overridden with a fake so
no AWS/LocalStack is needed.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import storage_dep
from app.ai.rag.vector_store import get_vector_store
from app.infra.db import set_engine
from app.main import app


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
    """TestClient with the engine set and S3 storage faked out."""
    app.dependency_overrides[storage_dep] = lambda: FakeStorage()
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
