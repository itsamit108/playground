"""Chat endpoint schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A note snippet used to ground an answer."""

    note_id: int | None = None
    note_title: str | None = None
    snippet: str
    score: float


class ChatRequest(BaseModel):
    """Ask a question grounded in the user's notes."""

    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = []
    model: str
    session_id: str | None = None
