"""Retrieval (semantic search) endpoint schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    """Semantic search over the user's notes."""

    query: str = Field(min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class RetrievalHit(BaseModel):
    note_id: int | None = None
    note_title: str | None = None
    snippet: str
    score: float


class RetrievalResponse(BaseModel):
    query: str
    hits: list[RetrievalHit]


class ReindexResponse(BaseModel):
    """Result of reindexing the user's notes into the vector store."""

    notes_indexed: int
    chunks_indexed: int
