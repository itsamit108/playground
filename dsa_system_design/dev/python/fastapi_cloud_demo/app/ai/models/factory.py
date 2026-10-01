"""LLM client factory.

Selects a provider from settings. Defaults to the offline ``EchoProvider`` so
the app runs with zero configuration. If a provider is requested but not usable
(e.g. ``openai`` without a key), it falls back to Echo rather than crashing.
"""

from __future__ import annotations

from app.ai.models.base import LLMClient
from app.ai.models.providers import (
    EchoProvider,
    OllamaProvider,
    OpenAICompatProvider,
)
from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_llm_client(settings: Settings) -> LLMClient:
    """Return an LLMClient implementation based on settings."""
    provider = (settings.llm_provider or "echo").lower()

    if provider == "openai":
        if settings.openai_api_key:
            return OpenAICompatProvider(
                base_url=settings.openai_base_url,
                api_key=settings.openai_api_key,
                model=settings.llm_model,
            )
        logger.warning("llm_provider=openai but no openai_api_key set; using EchoProvider")
        return EchoProvider(model=settings.llm_model)

    if provider == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.llm_model,
        )

    if provider != "echo":
        logger.warning("Unknown llm_provider=%s; using EchoProvider", provider)
    return EchoProvider(model=settings.llm_model)
