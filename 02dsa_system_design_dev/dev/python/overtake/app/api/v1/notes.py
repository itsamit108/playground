"""Notes CRUD endpoints (with search + pagination)."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, SessionDep, StorageDep
from app.schemas.common import (
    NoteCreate,
    NoteListResponse,
    NoteResponse,
    NoteUpdate,
)
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
)
def create_note(
    body: NoteCreate, current_user: CurrentUser, session: SessionDep
) -> NoteResponse:
    note = note_service.create_note(
        session,
        current_user,
        title=body.title,
        content=body.content,
        is_pinned=body.is_pinned,
    )
    return note_service.to_response(session, note)


@router.get("", response_model=NoteListResponse, summary="List notes")
def list_notes(
    current_user: CurrentUser,
    session: SessionDep,
    search: str | None = Query(default=None, description="Search title/content"),
    is_pinned: bool | None = Query(default=None, description="Filter pinned"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> NoteListResponse:
    notes, total = note_service.list_notes(
        session,
        current_user,
        search=search,
        is_pinned=is_pinned,
        page=page,
        page_size=page_size,
    )
    return NoteListResponse(
        notes=[note_service.to_response(session, n) for n in notes],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{note_id}", response_model=NoteResponse, summary="Get a note")
def get_note(
    note_id: int, current_user: CurrentUser, session: SessionDep
) -> NoteResponse:
    note = note_service.get_owned_note(session, note_id, current_user)
    return note_service.to_response(session, note)


@router.put("/{note_id}", response_model=NoteResponse, summary="Update a note")
def update_note(
    note_id: int,
    body: NoteUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> NoteResponse:
    note = note_service.update_note(
        session,
        current_user,
        note_id,
        title=body.title,
        content=body.content,
        is_pinned=body.is_pinned,
    )
    return note_service.to_response(session, note)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete a note and its attachments",
)
def delete_note(
    note_id: int,
    current_user: CurrentUser,
    session: SessionDep,
    storage: StorageDep,
) -> None:
    note_service.delete_note(session, current_user, note_id, storage)
