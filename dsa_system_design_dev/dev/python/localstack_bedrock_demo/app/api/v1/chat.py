"""Chat endpoints -> chat_service (the genuine end-to-end AI feature)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, ChatServiceDep
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[AuthDep])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, service: ChatServiceDep) -> ChatResponse:
    """Send a message and get a reply (multi-turn via session_id)."""
    return await service.chat(req)


@router.delete("/{session_id}", status_code=204)
async def reset_session(session_id: str, service: ChatServiceDep) -> None:
    """Clear a conversation session's history."""
    service.reset(session_id)
