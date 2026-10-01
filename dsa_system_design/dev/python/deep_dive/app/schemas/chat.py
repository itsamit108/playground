"""Chat request/response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    session_id: str | None = None
    model: str | None = None
    temperature: float = 0.2
    # When true, retrieve relevant ingested chunks and ground the answer (RAG).
    use_rag: bool = False


class ChatResponse(BaseModel):
    content: str
    model: str
    provider: str
    session_id: str | None = None
    sources: list[str] = Field(default_factory=list)
