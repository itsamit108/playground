"""Authentication use cases: register, login, fetch current user."""

from __future__ import annotations

from sqlmodel import Session, col, select

from app.core.config import Settings
from app.core.exceptions import AuthError, ConflictError
from app.core.security import create_access_token, hash_password, verify_password
from app.infra.db import User


def register_user(
    session: Session, *, username: str, email: str, password: str
) -> User:
    """Create a new user, enforcing username/email uniqueness."""
    existing = session.exec(
        select(User).where(
            (col(User.username) == username) | (col(User.email) == email)
        )
    ).first()
    if existing:
        raise ConflictError("Username or email already taken")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(
    session: Session, settings: Settings, *, username: str, password: str
) -> str:
    """Verify credentials and return a signed JWT."""
    user = session.exec(select(User).where(col(User.username) == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid credentials")
    return create_access_token(user.id, settings)  # type: ignore[arg-type]
