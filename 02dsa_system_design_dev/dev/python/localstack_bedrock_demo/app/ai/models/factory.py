"""LLM client factory with offline-first auto-fallback.

``get_llm_client(settings)`` returns a provider per ``settings.llm_provider``:

- "echo"    -> always the offline EchoProvider.
- "bedrock" -> always BedrockProvider (errors surface if unreachable).
- "auto"    -> BedrockProvider when LocalStack/Bedrock is reachable, else
               EchoProvider. This is the default so the service runs with no
               external services configured.
"""

from __future__ import annotations

from app.ai.models.base import LLMClient
from app.ai.models.providers import BedrockProvider, EchoProvider
from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_llm_client(settings: Settings) -> LLMClient:
    """Resolve the configured LLM client (async to allow a reachability probe)."""
    choice = (settings.llm_provider or "auto").lower()

    if choice == "echo":
        logger.info("LLM provider: echo (offline, forced)")
        return EchoProvider(default_model=settings.bedrock_model_id)

    if choice == "bedrock":
        logger.info("LLM provider: bedrock (forced)")
        return BedrockProvider(settings)

    # auto
    bedrock = BedrockProvider(settings)
    if await bedrock.is_reachable():
        logger.info("LLM provider: bedrock (auto-detected reachable)")
        return bedrock
    logger.info("LLM provider: echo (auto fallback; Bedrock unreachable)")
    return EchoProvider(default_model=settings.bedrock_model_id)


def get_offline_client(settings: Settings) -> LLMClient:
    """Return the EchoProvider synchronously (handy for tests / scripts)."""
    return EchoProvider(default_model=settings.bedrock_model_id)
