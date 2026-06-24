"""Shared FastAPI dependencies.

Wires services to providers. Routers depend on these; they never construct LLM
clients, agents, or stores themselves.
"""

from __future__ import annotations

from functools import lru_cache

from app.ai.models.factory import get_llm_client
from app.ai.tools.registry import registry
from app.core.config import Settings, get_settings
from app.services.agent_service import AgentService
from app.services.chat_service import ChatService
from app.services.counter_service import CounterService, counter_service
from app.services.eval_service import EvalService
from app.services.retrieval_service import RetrievalService, retrieval_service
from app.services.system_service import SystemService, system_service

# Importing builtins registers the function tools into the global registry.
import app.ai.tools.builtins  # noqa: F401


def get_app_settings() -> Settings:
    return get_settings()


def get_counter_service() -> CounterService:
    return counter_service


def get_system_service() -> SystemService:
    return system_service


def get_retrieval_service() -> RetrievalService:
    return retrieval_service


@lru_cache
def get_chat_service() -> ChatService:
    settings = get_settings()
    return ChatService(llm=get_llm_client(settings), settings=settings)


@lru_cache
def get_agent_service() -> AgentService:
    settings = get_settings()
    return AgentService(llm=get_llm_client(settings), tools=registry)


@lru_cache
def get_eval_service() -> EvalService:
    settings = get_settings()
    return EvalService(llm=get_llm_client(settings))
