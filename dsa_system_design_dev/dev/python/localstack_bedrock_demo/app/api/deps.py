"""Shared FastAPI dependencies.

Wires settings + the resolved LLM client into the service layer. Routers depend
only on these factories, never on AI SDKs directly (enforces api -> services ->
ai dependency direction).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.ai.models.base import LLMClient
from app.ai.models.factory import get_llm_client
from app.core.config import Settings, get_settings
from app.core.security import verify_api_key
from app.services.agent_service import AgentService
from app.services.chat_service import ChatService
from app.services.eval_service import EvalService
from app.services.retrieval_service import RetrievalService

SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_llm(settings: SettingsDep) -> LLMClient:
    """Resolve the configured LLM client (Bedrock or offline Echo)."""
    return await get_llm_client(settings)


LLMDep = Annotated[LLMClient, Depends(get_llm)]


def require_auth(
    settings: SettingsDep,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    """No-op when no API key configured; otherwise validates X-API-Key."""
    if not verify_api_key(settings, x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )


def get_chat_service(llm: LLMDep, settings: SettingsDep) -> ChatService:
    return ChatService(llm=llm, settings=settings)


def get_agent_service(llm: LLMDep, settings: SettingsDep) -> AgentService:
    return AgentService(llm=llm, settings=settings)


def get_retrieval_service() -> RetrievalService:
    return RetrievalService()


def get_eval_service(llm: LLMDep) -> EvalService:
    return EvalService(llm=llm)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]
RetrievalServiceDep = Annotated[RetrievalService, Depends(get_retrieval_service)]
EvalServiceDep = Annotated[EvalService, Depends(get_eval_service)]
AuthDep = Depends(require_auth)
