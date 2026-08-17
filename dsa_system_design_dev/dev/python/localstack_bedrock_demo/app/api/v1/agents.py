"""Agent endpoints -> agent_service."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AgentServiceDep, AuthDep
from app.schemas.agents import AgentRunRequest, AgentRunResponse

router = APIRouter(prefix="/agents", tags=["agents"], dependencies=[AuthDep])


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(req: AgentRunRequest, service: AgentServiceDep) -> AgentRunResponse:
    """Run the tool-using agent workflow against a goal."""
    return await service.run(req)


@router.get("/tools")
async def list_tools(service: AgentServiceDep) -> list[dict]:
    """List the tools the agent can call (with schemas/permissions)."""
    return service.available_tools()
