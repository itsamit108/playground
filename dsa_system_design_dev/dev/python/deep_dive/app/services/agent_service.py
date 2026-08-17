"""Agent service — runs agent workflows from ``ai/agents``."""

from __future__ import annotations

from app.ai.agents.state import RunState
from app.ai.agents.workflows import SummarizeAgent
from app.ai.models.base import LLMClient
from app.core.config import Settings
from app.schemas.agents import AgentRunRequest, AgentRunResponse, AgentStep


def _to_steps(state: RunState) -> list[AgentStep]:
    return [
        AgentStep(name=s.name, status=s.status.value, detail=s.detail) for s in state.steps
    ]


class AgentService:
    def __init__(self, llm: LLMClient, settings: Settings):
        self.llm = llm
        self.settings = settings

    async def run(self, req: AgentRunRequest) -> AgentRunResponse:
        """Run the generic summarize workflow (a demonstration agent).

        The flagship EPUB conversion workflow is driven through
        ``ConversionService`` because it involves file upload + background jobs.
        """
        agent = SummarizeAgent(self.llm)
        state = await agent.run(req.goal, req.inputs)
        return AgentRunResponse(
            workflow=agent.name,
            status="failed" if state.failed else "completed",
            output=state.output,
            steps=_to_steps(state),
        )
