"""Agent service: run the NotesOrganizer agent over a user's notes."""

from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session

from app.ai.agents.state import AgentState
from app.ai.agents.workflows import NotesOrganizerAgent
from app.ai.models.factory import get_llm_client
from app.core.config import Settings, get_settings
from app.infra.db import User
from app.infra.observability import span
from app.services import note_service


@dataclass
class AgentRunResult:
    answer: str
    status: str
    steps: list[str]
    tool_calls: list[dict]


async def run_agent(
    session: Session,
    user: User,
    *,
    task: str,
    top_k: int | None = None,
    settings: Settings | None = None,
) -> AgentRunResult:
    """Index the user's notes, then run the organizer agent on `task`."""
    settings = settings or get_settings()

    # Make sure the agent's search_notes tool has fresh data.
    note_service.reindex_user_notes(session, user)

    llm = get_llm_client(settings)
    agent = NotesOrganizerAgent(llm, top_k=top_k or settings.rag_top_k)
    state = AgentState(user_id=user.id, task=task)  # type: ignore[arg-type]

    with span("agent.run", user_id=user.id):
        await agent.run(state)

    return AgentRunResult(
        answer=state.answer,
        status=state.status.value,
        steps=state.steps,
        tool_calls=[
            {
                "name": tc.name,
                "arguments": tc.arguments,
                "result_count": len(tc.result) if isinstance(tc.result, list) else None,
            }
            for tc in state.tool_calls
        ],
    )
