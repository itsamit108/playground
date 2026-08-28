"""Retrieval endpoints: semantic search + reindex over the user's notes."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.retrieval import (
    ReindexResponse,
    RetrievalHit,
    RetrievalRequest,
    RetrievalResponse,
)
from app.services import note_service, retrieval_service

router = APIRouter(prefix="/retrieval", tags=["AI: Retrieval"])


@router.post("/search", response_model=RetrievalResponse, summary="Semantic search")
def search(
    body: RetrievalRequest, current_user: CurrentUser, session: SessionDep
) -> RetrievalResponse:
    chunks = retrieval_service.search(
        session, current_user, query=body.query, top_k=body.top_k
    )
    return RetrievalResponse(
        query=body.query,
        hits=[
            RetrievalHit(
                note_id=c.note_id,
                note_title=c.note_title,
                snippet=c.text,
                score=c.score,
            )
            for c in chunks
        ],
    )


@router.post(
    "/reindex",
    response_model=ReindexResponse,
    summary="Rebuild the vector index for your notes",
)
def reindex(current_user: CurrentUser, session: SessionDep) -> ReindexResponse:
    notes, chunks = note_service.reindex_user_notes(session, current_user)
    return ReindexResponse(notes_indexed=notes, chunks_indexed=chunks)
