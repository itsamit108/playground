"""Agent endpoints: summarize / organize your notes via the agent workflow."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep, SettingsDep
from app.schemas.agents import AgentRequest, AgentResponse, AgentToolCall
from app.services import agent_service

router = APIRouter(prefix="/agents", tags=["AI: Agents"])


@router.post(
    "/organize",
    response_model=AgentResponse,
    summary="Run the notes-organizer agent",
)
async def organize(
    body: AgentRequest,
    current_user: CurrentUser,
    session: SessionDep,
    settings: SettingsDep,
) -> AgentResponse:
    result = await agent_service.run_agent(
        session, current_user, task=body.task, top_k=body.top_k, settings=settings
    )
    return AgentResponse(
        answer=result.answer,
        status=result.status,
        steps=result.steps,
        tool_calls=[
            AgentToolCall(
                name=tc["name"],
                arguments=tc["arguments"],
                result_count=tc.get("result_count"),
            )
            for tc in result.tool_calls
        ],
    )
