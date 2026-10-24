"""Base agent abstraction (plan / act / respond).

A small, custom orchestration base so the agent layer is genuinely usable without
pulling a heavy framework. Concrete workflows subclass this; the plan/act/respond
loop is intentionally explicit so it maps cleanly onto LangGraph nodes or the
OpenAI Agents SDK later.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.ai.agents.state import RunState
from app.ai.models.base import LLMClient


class BaseAgent(ABC):
    name: str = "agent"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    @abstractmethod
    async def plan(self, state: RunState) -> list[str]:
        """Return an ordered list of step names to execute."""

    @abstractmethod
    async def act(self, step: str, state: RunState) -> None:
        """Execute a single step, mutating ``state``."""

    async def respond(self, state: RunState) -> dict[str, Any]:
        """Produce the final output dict from the accumulated state."""
        return state.output

    async def run(self, goal: str, inputs: dict[str, Any] | None = None) -> RunState:
        state = RunState(goal=goal, inputs=inputs or {})
        plan = await self.plan(state)
        for step in plan:
            try:
                await self.act(step, state)
            except Exception as exc:  # surface per-step failures into state
                from app.ai.agents.state import StepStatus

                state.record(step, status=StepStatus.ERROR, detail=str(exc))
                break
        state.output = await self.respond(state)
        return state
