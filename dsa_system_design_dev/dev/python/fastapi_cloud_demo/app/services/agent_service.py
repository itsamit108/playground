"""Agent service.

Drives the OpsAssistant agent workflow. The router calls this; it never touches
agent internals or the LLM SDK directly.
"""

from __future__ import annotations

from app.ai.agents.workflows import OpsAssistantAgent
from app.ai.models.base import LLMClient
from app.ai.tools.registry import ToolRegistry


class AgentService:
    """Application service exposing agent workflows."""

    def __init__(self, llm: LLMClient, tools: ToolRegistry) -> None:
        self._agent = OpsAssistantAgent(llm=llm, tools=tools)

    async def run_ops_assistant(self, objective: str) -> dict:
        state = await self._agent.run(objective)
        return {
            "objective": state.objective,
            "answer": state.answer or "",
            "steps": state.steps,
            "tool_calls": [
                {"name": call.name, "arguments": call.arguments, "result": call.result}
                for call in state.tool_calls
            ],
        }
