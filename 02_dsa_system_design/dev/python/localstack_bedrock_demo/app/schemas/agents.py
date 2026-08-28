"""Agent request/response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    goal: str = Field(..., min_length=1, description="What the agent should do.")


class AgentToolCall(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}
    result: Any = None


class AgentRunResponse(BaseModel):
    goal: str
    steps: list[str]
    tool_calls: list[AgentToolCall]
    answer: str
