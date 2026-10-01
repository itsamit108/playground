"""Database adapter (placeholder).

This app keeps job state in memory (see ``services/conversion_service.py``) and
needs no relational DB by default. This module documents the extension point: a
SQLAlchemy engine / session factory would live here, with Alembic migrations in
``migrations/``.
"""

from __future__ import annotations


def get_engine():  # pragma: no cover - extension point
    raise NotImplementedError(
        "No database configured. Add SQLAlchemy engine setup here if persistence is needed."
    )
