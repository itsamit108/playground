"""Shared FastAPI dependencies: settings, db session, storage, current user."""

from __future__ import annotations

from typing import Annotated, Iterator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthError
from app.core.security import decode_access_token
from app.infra.db import User, get_session
from app.infra.storage import S3Storage, get_storage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_settings_dep() -> Settings:
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]


def db_session() -> Iterator[Session]:
    yield from get_session()


SessionDep = Annotated[Session, Depends(db_session)]


def storage_dep(settings: SettingsDep) -> S3Storage:
    return get_storage(settings)


StorageDep = Annotated[S3Storage, Depends(storage_dep)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
    settings: SettingsDep,
) -> User:
    """Resolve the authenticated user from the bearer token."""
    user_id = decode_access_token(token, settings)
    if user_id is None:
        raise AuthError("Invalid or expired token")
    user = session.get(User, user_id)
    if not user:
        raise AuthError("User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
