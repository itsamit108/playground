"""Chat request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message.")
    session_id: str = Field(
        default="default", description="Conversation session id (memory key)."
    )
    model: str | None = Field(default=None, description="Override model id.")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    system_prompt: str | None = Field(
        default=None, description="Override the system prompt for this turn."
    )


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0


class ChatResponse(BaseModel):
    reply: str
    model: str
    provider: str
    session_id: str
    turn: int
    usage: Usage
