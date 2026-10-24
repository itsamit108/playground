"""Attachment use cases: upload, list, download, delete (S3-backed)."""

from __future__ import annotations

import os
import uuid
from typing import Sequence

from sqlmodel import Session, col, select

from app.core.exceptions import NotFoundError
from app.infra.db import Attachment, Note, User
from app.infra.storage import S3Storage
from app.services.note_service import get_owned_note


def _get_owned_attachment(
    session: Session, attachment_id: int, user: User
) -> Attachment:
    attachment = session.get(Attachment, attachment_id)
    if not attachment:
        raise NotFoundError("Attachment not found")
    note = session.get(Note, attachment.note_id)
    if not note or note.user_id != user.id:
        raise NotFoundError("Attachment not found")
    return attachment


def upload_attachment(
    session: Session,
    user: User,
    note_id: int,
    storage: S3Storage,
    *,
    filename: str,
    content_type: str,
    data: bytes,
) -> Attachment:
    note = get_owned_note(session, note_id, user)
    ext = os.path.splitext(filename)[1]
    s3_key = f"users/{user.id}/notes/{note.id}/{uuid.uuid4().hex}{ext}"
    storage.put(s3_key, data, content_type)

    attachment = Attachment(
        filename=filename,
        s3_key=s3_key,
        content_type=content_type,
        size_bytes=len(data),
        note_id=note.id,  # type: ignore[arg-type]
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return attachment


def list_attachments(
    session: Session, user: User, note_id: int
) -> Sequence[Attachment]:
    note = get_owned_note(session, note_id, user)
    return session.exec(
        select(Attachment).where(col(Attachment.note_id) == note.id)
    ).all()


def get_attachment_bytes(
    session: Session, user: User, attachment_id: int, storage: S3Storage
) -> tuple[Attachment, bytes]:
    attachment = _get_owned_attachment(session, attachment_id, user)
    try:
        data = storage.get(attachment.s3_key)
    except Exception as exc:  # noqa: BLE001
        raise NotFoundError("File not found in storage") from exc
    return attachment, data


def delete_attachment(
    session: Session, user: User, attachment_id: int, storage: S3Storage
) -> None:
    attachment = _get_owned_attachment(session, attachment_id, user)
    storage.delete(attachment.s3_key)
    session.delete(attachment)
    session.commit()
