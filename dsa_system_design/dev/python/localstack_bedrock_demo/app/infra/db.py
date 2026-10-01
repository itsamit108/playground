"""Database adapter (placeholder).

This service has no relational DB by default. This module is the seam where a
SQLAlchemy / async engine would live. ``migrations/`` is reserved for Alembic.
"""

from __future__ import annotations


def get_engine() -> None:
    """No DB configured. Returns None; wire SQLAlchemy here when needed."""
    return None
