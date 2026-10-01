"""LLM client factory.

Selects a provider from settings. Defaults to the offline `EchoProvider`
whenever no provider/API key is configured, so the app runs with zero keys.
"""

from __future__ import annotations

from app.ai.models.base import LLMClient
from app.ai.models.providers import (
    AnthropicProvider,
    EchoProvider,
    OpenAIProvider,
)
from app.core.config import Settings, get_settings


def get_llm_client(settings: Settings | None = None) -> LLMClient:
    """Return an LLMClient for the configured provider (echo by default)."""
    settings = settings or get_settings()
    provider = (settings.llm_provider or "echo").lower()

    if provider in ("", "echo"):
        return EchoProvider()

    # Real providers require an API key; fall back to echo if missing so the
    # app never crashes for lack of credentials.
    if not settings.llm_api_key:
        return EchoProvider()

    if provider == "openai":
        return OpenAIProvider(settings.llm_api_key, settings.llm_model)
    if provider == "anthropic":
        return AnthropicProvider(settings.llm_api_key, settings.llm_model)

    return EchoProvider()
