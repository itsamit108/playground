"""Database adapter (placeholder).

This demo has no relational database. This module documents where a DB engine /
session factory (SQLAlchemy + Alembic migrations) would live. The ORM models
would go in ``schemas/`` or here -- never in a ``domain/`` package.
"""

from __future__ import annotations


def get_db() -> None:
    """No database configured for this demo. Wire SQLAlchemy here if needed."""
    return None
