"""Database engine, session factory, and SQLModel ORM models.

The ORM models (User, Note, Attachment) live here per the conversion spec
(no DDD: ORM goes in infra, request/response shapes go in app/schemas).

The engine is created lazily from settings so tests can point at an
in-memory SQLite database before anything connects to PostgreSQL.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterator, Optional

from sqlalchemy import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

from app.core.config import get_settings


# ── ORM models ────────────────────────────────────────────────────────────
class User(SQLModel, table=True):
    """Application user."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=64)
    email: str = Field(index=True, unique=True, max_length=256)
    hashed_password: str = Field(max_length=256)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    notes: list["Note"] = Relationship(back_populates="owner", cascade_delete=True)


class Note(SQLModel, table=True):
    """A user's note: rich text content plus multimedia attachments."""

    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=256)
    content: str = Field(default="")
    is_pinned: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_id: int = Field(foreign_key="users.id", index=True)

    owner: Optional["User"] = Relationship(back_populates="notes")
    attachments: list["Attachment"] = Relationship(
        back_populates="note", cascade_delete=True
    )


class Attachment(SQLModel, table=True):
    """A multimedia file attached to a note, stored in S3."""

    __tablename__ = "attachments"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=512)
    s3_key: str = Field(max_length=1024)
    content_type: str = Field(default="application/octet-stream", max_length=128)
    size_bytes: int = Field(default=0)
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    note_id: int = Field(foreign_key="notes.id", index=True)

    note: Optional["Note"] = Relationship(back_populates="attachments")


# ── Engine / session management ─────────────────────────────────────────────
_engine: Engine | None = None


def _build_engine(database_url: str) -> Engine:
    """Create an engine, applying SQLite-friendly options when needed."""
    if database_url.startswith("sqlite"):
        # In-memory SQLite shared across threads/connections for tests.
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )
    return create_engine(database_url, echo=False)


def get_engine() -> Engine:
    """Return the lazily-created process-wide engine."""
    global _engine
    if _engine is None:
        _engine = _build_engine(get_settings().database_url)
    return _engine


def set_engine(engine: Engine) -> None:
    """Override the engine (used by the test suite)."""
    global _engine
    _engine = engine


def init_db() -> None:
    """Create all tables on the active engine."""
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    """Yield a SQLModel session bound to the active engine (FastAPI dependency)."""
    with Session(get_engine()) as session:
        yield session
