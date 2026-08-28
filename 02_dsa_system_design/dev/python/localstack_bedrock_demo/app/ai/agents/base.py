"""Base agent abstraction: plan -> act -> respond.

Lightweight, framework-agnostic. In production this layer is where Pydantic AI
/ LangGraph / OpenAI Agents SDK would live; the contract stays the same.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.agents.state import AgentState
from app.ai.models.base import LLMClient
from app.ai.tools.registry import ToolRegistry


class BaseAgent(ABC):
    """Abstract single-agent plan/act/respond loop."""

    def __init__(self, llm: LLMClient, tools: ToolRegistry) -> None:
        self.llm = llm
        self.tools = tools

    @abstractmethod
    async def plan(self, state: AgentState) -> list[str]:
        """Produce an ordered list of step descriptions for the goal."""

    @abstractmethod
    async def act(self, state: AgentState) -> None:
        """Execute the plan, recording tool calls into state."""

    @abstractmethod
    async def respond(self, state: AgentState) -> str:
        """Produce the final natural-language answer."""

    async def run(self, goal: str) -> AgentState:
        """Run the full loop and return the resulting state."""
        state = AgentState(goal=goal)
        for step in await self.plan(state):
            state.record_step(step)
        await self.act(state)
        state.final_answer = await self.respond(state)
        return state
