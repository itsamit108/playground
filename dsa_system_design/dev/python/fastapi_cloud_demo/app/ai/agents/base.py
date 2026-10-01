"""Base agent abstraction: a simple plan/act/respond loop.

This is a deliberately small, framework-agnostic orchestration base. In a larger
system this is exactly where Pydantic AI / LangGraph / OpenAI Agents SDK would
implement the same plan/act/respond contract (see README ecosystem mapping).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.agents.state import AgentState
from app.ai.models.base import LLMClient
from app.ai.tools.registry import ToolRegistry


class BaseAgent(ABC):
    """Abstract agent with a plan -> act -> respond lifecycle."""

    def __init__(self, llm: LLMClient, tools: ToolRegistry) -> None:
        self.llm = llm
        self.tools = tools

    @abstractmethod
    async def plan(self, state: AgentState) -> None:
        """Decide which tools (if any) to use; mutate state."""

    @abstractmethod
    async def act(self, state: AgentState) -> None:
        """Execute the plan (call tools); record results in state."""

    @abstractmethod
    async def respond(self, state: AgentState) -> str:
        """Produce the final answer from gathered state."""

    async def run(self, objective: str) -> AgentState:
        """Execute the full lifecycle and return the final state."""
        state = AgentState(objective=objective)
        await self.plan(state)
        await self.act(state)
        state.answer = await self.respond(state)
        return state
