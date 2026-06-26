"""Built-in function tools.

- ``list_models``: wraps Bedrock ``list-foundation-models`` (control plane) so
  the agent can answer "what models are available?". Falls back to a static
  offline list when LocalStack/Bedrock is unreachable, so it works with no
  external services.
- ``echo``: trivial deterministic tool useful for tests/demos.
"""

from __future__ import annotations

from typing import Any

from app.ai.tools.registry import Tool, ToolRegistry
from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_OFFLINE_MODELS = [
    {"modelId": "ollama.llama3.2", "providerName": "Ollama", "modelName": "Llama 3.2"},
    {"modelId": "echo-1", "providerName": "Offline", "modelName": "Echo Provider"},
]


def list_models(settings: Settings) -> list[dict[str, Any]]:
    """List Bedrock foundation models; fall back to a static list offline.

    In offline (``echo``) mode we skip the boto call entirely so the tool — and
    any test that exercises it — is instant and deterministic with no network.
    """
    if (settings.llm_provider or "").lower() == "echo":
        return _OFFLINE_MODELS
    try:
        from app.ai.models.providers import BedrockProvider

        client = BedrockProvider(settings).control_plane_client()
        resp = client.list_foundation_models()
        models = resp.get("modelSummaries", [])
        return [
            {
                "modelId": m.get("modelId", "?"),
                "providerName": m.get("providerName", "?"),
                "modelName": m.get("modelName", "?"),
            }
            for m in models
        ] or _OFFLINE_MODELS
    except Exception as exc:  # noqa: BLE001 - offline fallback
        logger.info("list_models falling back to offline list: %s", exc)
        return _OFFLINE_MODELS


def echo(text: str) -> str:
    """Return the text unchanged (demo/test tool)."""
    return text


def build_default_registry(settings: Settings) -> ToolRegistry:
    """Construct a ToolRegistry populated with the built-in tools."""
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="list_models",
            description="List available Bedrock foundation models.",
            func=lambda: list_models(settings),
            parameters={"type": "object", "properties": {}},
        )
    )
    registry.register(
        Tool(
            name="echo",
            description="Echo the provided text back.",
            func=echo,
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        )
    )
    return registry
