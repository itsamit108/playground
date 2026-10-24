"""Chat endpoints -> chat_service."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import ChatServiceDep, require_auth
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(require_auth)])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, service: ChatServiceDep) -> ChatResponse:
    return await service.chat(req)
