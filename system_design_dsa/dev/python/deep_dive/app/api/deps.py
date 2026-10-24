"""Shared FastAPI dependencies.

Wires settings -> LLM client -> services. Routers depend only on these factories,
keeping LLM SDKs and orchestration out of the api layer.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.ai.models.base import LLMClient
from app.ai.models.factory import get_llm_client
from app.core.config import Settings, get_settings
from app.core.security import api_key_header, verify_api_key
from app.services.agent_service import AgentService
from app.services.chat_service import ChatService
from app.services.conversion_service import ConversionService
from app.services.eval_service import EvalService
from app.services.retrieval_service import RetrievalService

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_llm(settings: SettingsDep) -> LLMClient:
    return get_llm_client(settings)


LLMDep = Annotated[LLMClient, Depends(get_llm)]


def require_auth(settings: SettingsDep, provided: Annotated[str | None, Depends(api_key_header)]) -> None:
    verify_api_key(settings, provided)


def get_chat_service(llm: LLMDep, settings: SettingsDep) -> ChatService:
    return ChatService(llm, settings)


def get_agent_service(llm: LLMDep, settings: SettingsDep) -> AgentService:
    return AgentService(llm, settings)


def get_conversion_service(llm: LLMDep, settings: SettingsDep) -> ConversionService:
    return ConversionService(llm, settings)


def get_retrieval_service(settings: SettingsDep) -> RetrievalService:
    return RetrievalService(settings)


def get_eval_service(llm: LLMDep, settings: SettingsDep) -> EvalService:
    return EvalService(llm, settings)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]
ConversionServiceDep = Annotated[ConversionService, Depends(get_conversion_service)]
RetrievalServiceDep = Annotated[RetrievalService, Depends(get_retrieval_service)]
EvalServiceDep = Annotated[EvalService, Depends(get_eval_service)]
