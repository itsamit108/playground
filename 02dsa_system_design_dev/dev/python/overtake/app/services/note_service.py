"""Note use cases: CRUD + search/pagination, with RAG index sync.

On create/update the note is (re)indexed into the vector store; on delete its
chunks and S3 attachments are removed. This keeps the AI features grounded in
current data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlmodel import Session, col, select

from app.ai.rag.retriever import Retriever
from app.core.exceptions import NotFoundError
from app.infra.db import Attachment, Note, User
from app.infra.storage import S3Storage
from app.schemas.common import AttachmentResponse, NoteResponse


# ── Helpers ─────────────────────────────────────────────────────────────────
def get_owned_note(session: Session, note_id: int, user: User) -> Note:
    """Fetch a note owned by `user` or raise NotFound."""
    note = session.get(Note, note_id)
    if not note or note.user_id != user.id:
        raise NotFoundError("Note not found")
    return note


def to_response(session: Session, note: Note) -> NoteResponse:
    """Serialize a Note (with attachments) into a NoteResponse."""
    attachments = session.exec(
        select(Attachment).where(col(Attachment.note_id) == note.id)
    ).all()
    return NoteResponse(
        id=note.id,  # type: ignore[arg-type]
        title=note.title,
        content=note.content,
        is_pinned=note.is_pinned,
        created_at=note.created_at,
        updated_at=note.updated_at,
        attachments=[
            AttachmentResponse(
                id=a.id,  # type: ignore[arg-type]
                filename=a.filename,
                content_type=a.content_type,
                size_bytes=a.size_bytes,
                uploaded_at=a.uploaded_at,
            )
            for a in attachments
        ],
    )


def _index(note: Note) -> None:
    Retriever().index_note(
        user_id=note.user_id,
        note_id=note.id,  # type: ignore[arg-type]
        title=note.title,
        content=note.content,
    )


# ── Use cases ───────────────────────────────────────────────────────────────
def create_note(
    session: Session, user: User, *, title: str, content: str, is_pinned: bool
) -> Note:
    note = Note(
        title=title, content=content, is_pinned=is_pinned, user_id=user.id  # type: ignore[arg-type]
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    _index(note)
    return note


def list_notes(
    session: Session,
    user: User,
    *,
    search: str | None,
    is_pinned: bool | None,
    page: int,
    page_size: int,
) -> tuple[Sequence[Note], int]:
    """Return a page of the user's notes plus the total match count."""
    stmt = select(Note).where(col(Note.user_id) == user.id)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            col(Note.title).ilike(pattern) | col(Note.content).ilike(pattern)
        )
    if is_pinned is not None:
        stmt = stmt.where(col(Note.is_pinned) == is_pinned)

    total = len(session.exec(stmt).all())
    stmt = stmt.order_by(col(Note.updated_at).desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    return session.exec(stmt).all(), total


def update_note(
    session: Session,
    user: User,
    note_id: int,
    *,
    title: str | None,
    content: str | None,
    is_pinned: bool | None,
) -> Note:
    note = get_owned_note(session, note_id, user)
    if title is not None:
        note.title = title
    if content is not None:
        note.content = content
    if is_pinned is not None:
        note.is_pinned = is_pinned
    note.updated_at = datetime.now(timezone.utc)
    session.add(note)
    session.commit()
    session.refresh(note)
    _index(note)
    return note


def delete_note(
    session: Session, user: User, note_id: int, storage: S3Storage
) -> None:
    note = get_owned_note(session, note_id, user)
    attachments = session.exec(
        select(Attachment).where(col(Attachment.note_id) == note.id)
    ).all()
    for att in attachments:
        storage.delete(att.s3_key)
    Retriever().remove_note(note.id)  # type: ignore[arg-type]
    session.delete(note)
    session.commit()


def reindex_user_notes(session: Session, user: User) -> tuple[int, int]:
    """Rebuild the vector index for all of a user's notes.

    Returns (notes_indexed, chunks_indexed).
    """
    notes = session.exec(select(Note).where(col(Note.user_id) == user.id)).all()
    retriever = Retriever()
    total_chunks = 0
    for note in notes:
        total_chunks += retriever.index_note(
            user_id=note.user_id,
            note_id=note.id,  # type: ignore[arg-type]
            title=note.title,
            content=note.content,
        )
    return len(notes), total_chunks
