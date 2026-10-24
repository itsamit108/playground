"""Agent endpoint schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Ask the agent to summarize or organize notes for a topic/task."""

    task: str = Field(min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class AgentToolCall(BaseModel):
    name: str
    arguments: dict
    result_count: int | None = None


class AgentResponse(BaseModel):
    answer: str
    status: str
    steps: list[str]
    tool_calls: list[AgentToolCall] = []
