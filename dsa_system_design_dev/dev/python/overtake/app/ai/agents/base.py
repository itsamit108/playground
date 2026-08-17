"""BaseAgent abstraction: a simple plan -> act -> respond loop.

This is intentionally framework-agnostic. In production this layer is where
Pydantic AI / LangGraph / OpenAI Agents SDK / CrewAI would plug in (see the
architecture doc's ecosystem table); here we provide a clean custom loop so the
agent works fully offline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.agents.state import AgentState, RunStatus
from app.ai.models.base import LLMClient


class BaseAgent(ABC):
    """Abstract agent with a plan/act/respond lifecycle."""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    @abstractmethod
    async def plan(self, state: AgentState) -> None:
        """Decide what to do; may populate state.steps."""

    @abstractmethod
    async def act(self, state: AgentState) -> None:
        """Call tools / gather context; may populate state.tool_calls."""

    @abstractmethod
    async def respond(self, state: AgentState) -> None:
        """Produce the final answer into state.answer."""

    async def run(self, state: AgentState) -> AgentState:
        """Execute the full lifecycle, tracking status."""
        state.status = RunStatus.RUNNING
        try:
            await self.plan(state)
            await self.act(state)
            await self.respond(state)
            state.status = RunStatus.DONE
        except Exception as exc:  # noqa: BLE001 - surface failure in state
            state.status = RunStatus.FAILED
            state.answer = f"Agent failed: {exc}"
        return state
