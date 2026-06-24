"""Agent request/response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    objective: str = Field(..., min_length=1, description="What the agent should do")


class AgentToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]
    result: Any


class AgentResponse(BaseModel):
    objective: str
    answer: str
    steps: list[str]
    tool_calls: list[AgentToolCall]
