"""Chat endpoints -> chat_service. No LLM SDK imports here."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_chat_service
from app.core.security import require_api_key
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, dependencies=[Depends(require_api_key)])
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    result = await service.chat(
        request.message,
        session_id=request.session_id,
        temperature=request.temperature,
    )
    return ChatResponse(**result)
