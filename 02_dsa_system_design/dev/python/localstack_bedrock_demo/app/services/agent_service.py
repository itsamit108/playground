"""Agent use case: drives the tool-using agent workflow."""

from __future__ import annotations

from app.ai.agents.workflows import ModelInfoAgent
from app.ai.models.base import LLMClient
from app.ai.tools.builtins import build_default_registry
from app.core.config import Settings
from app.schemas.agents import AgentRunRequest, AgentRunResponse, AgentToolCall


class AgentService:
    def __init__(self, llm: LLMClient, settings: Settings) -> None:
        self.llm = llm
        self.settings = settings
        self.registry = build_default_registry(settings)

    async def run(self, req: AgentRunRequest) -> AgentRunResponse:
        agent = ModelInfoAgent(self.llm, self.registry)
        state = await agent.run(req.goal)
        return AgentRunResponse(
            goal=state.goal,
            steps=state.steps,
            tool_calls=[
                AgentToolCall(tool=c.tool, arguments=c.arguments, result=c.result)
                for c in state.tool_calls
            ],
            answer=state.final_answer or "",
        )

    def available_tools(self) -> list[dict]:
        return self.registry.schemas()
