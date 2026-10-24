"""Agent endpoints -> agent_service. No agent orchestration here."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_agent_service
from app.core.security import require_api_key
from app.schemas.agents import AgentRequest, AgentResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post(
    "/ops-assistant",
    response_model=AgentResponse,
    dependencies=[Depends(require_api_key)],
)
async def ops_assistant(
    request: AgentRequest,
    service: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    result = await service.run_ops_assistant(request.objective)
    return AgentResponse(**result)
