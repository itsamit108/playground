"""Retrieval service: semantic search over a user's notes (RAG retrieval step).

Ensures the user's notes are indexed, then retrieves relevant chunks.
"""

from __future__ import annotations

from sqlmodel import Session

from app.ai.rag.retriever import Retriever, RetrievedChunk
from app.infra.db import User
from app.services import note_service


def search(
    session: Session, user: User, *, query: str, top_k: int | None = None
) -> list[RetrievedChunk]:
    """Retrieve relevant note chunks for a query, indexing on demand."""
    # Lazily (re)index the user's notes so search reflects current data.
    note_service.reindex_user_notes(session, user)
    retriever = Retriever()
    return retriever.retrieve(user_id=user.id, query=query, top_k=top_k)  # type: ignore[arg-type]
