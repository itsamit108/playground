"""Provider factory — selects an ``LLMClient`` based on configuration.

Offline-first: if no Google/Gemini key is configured (or the SDK is missing),
the factory returns the deterministic ``EchoProvider`` so the app always runs.
"""

from __future__ import annotations

from app.ai.models.base import LLMClient
from app.ai.models.providers import EchoProvider, GeminiProvider
from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_llm_client(settings: Settings) -> LLMClient:
    """Return a concrete ``LLMClient`` per configuration.

    ``llm_provider``:
      * "echo"   -> always EchoProvider
      * "gemini" -> GeminiProvider (falls back to Echo if no key/SDK)
      * "auto"   -> Gemini when a key is present, else Echo
    """
    provider = (settings.llm_provider or "auto").lower()

    if provider == "echo":
        return EchoProvider()

    if provider in ("gemini", "google", "auto"):
        if settings.has_llm_key:
            try:
                return GeminiProvider(
                    api_key=settings.resolved_google_key,
                    default_model=settings.llm_model,
                )
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Gemini unavailable (%s); falling back to EchoProvider.", exc)
                return EchoProvider()
        if provider != "auto":
            logger.warning("Provider %r requested but no API key set; using EchoProvider.", provider)
        return EchoProvider()

    logger.warning("Unknown llm_provider %r; using EchoProvider.", provider)
    return EchoProvider()
