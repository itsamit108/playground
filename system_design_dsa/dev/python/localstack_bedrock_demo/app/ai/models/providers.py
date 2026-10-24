"""Concrete LLM providers implementing the ``LLMClient`` contract.

- ``BedrockProvider``: wraps boto3 ``bedrock-runtime.converse`` pointed at the
  LocalStack endpoint (folds in the old ``chatbot/client.py`` +
  ``chatbot/conversation.py`` Converse logic).
- ``EchoProvider``: deterministic, offline, no network — the default fallback
  so the service and all tests run with zero external services.

Both return a normalised dict: ``{"text": str, "model": str, "usage": dict,
"raw": Any}``.
"""

from __future__ import annotations

import asyncio
from typing import Any, Sequence

from app.ai.models.base import (
    extract_system_prompt,
    to_bedrock_messages,
)
from app.core.config import Settings
from app.core.exceptions import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class EchoProvider:
    """Offline deterministic provider.

    Echoes the last user message with a short prefix. Used for local dev,
    CI, and tests so nothing requires LocalStack / Bedrock / Ollama.
    """

    name = "echo"

    def __init__(self, default_model: str = "echo-1") -> None:
        self._default_model = default_model

    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict:
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = str(m.get("content", ""))
                break
        text = f"Echo: {last_user}" if last_user else "Echo: (no input)"
        return {
            "text": text,
            "model": model or self._default_model,
            "usage": {
                "input_tokens": len(last_user.split()),
                "output_tokens": len(text.split()),
            },
            "raw": None,
        }


class BedrockProvider:
    """LLMClient backed by Bedrock Converse via boto3 (LocalStack endpoint)."""

    name = "bedrock"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._default_model = settings.bedrock_model_id
        self._default_system = settings.system_prompt
        self._runtime = None  # lazy boto3 client

    # ── boto3 client factories (folded from chatbot/client.py) ───

    def _runtime_client(self):
        if self._runtime is None:
            import boto3
            from botocore.config import Config

            s = self._settings
            self._runtime = boto3.client(
                "bedrock-runtime",
                endpoint_url=s.aws_endpoint_url,
                region_name=s.aws_region,
                aws_access_key_id=s.aws_access_key_id,
                aws_secret_access_key=s.aws_secret_access_key,
                config=Config(
                    retries={"max_attempts": 3, "mode": "adaptive"},
                    read_timeout=600,
                    connect_timeout=s.bedrock_connect_timeout,
                ),
            )
        return self._runtime

    def control_plane_client(self):
        """Return a boto3 ``bedrock`` control-plane client (for tools).

        Configured to FAIL FAST (single attempt, short timeouts) so that when
        LocalStack/Bedrock is down, the reachability probe and the ``list_models``
        tool degrade in ~a few seconds instead of retrying for ~30s.
        """
        import boto3
        from botocore.config import Config

        s = self._settings
        return boto3.client(
            "bedrock",
            endpoint_url=s.aws_endpoint_url,
            region_name=s.aws_region,
            aws_access_key_id=s.aws_access_key_id,
            aws_secret_access_key=s.aws_secret_access_key,
            config=Config(
                retries={"max_attempts": 1},
                connect_timeout=s.bedrock_connect_timeout,
                read_timeout=s.bedrock_connect_timeout,
            ),
        )

    # ── contract ─────────────────────────────────────────────────

    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict:
        model_id = model or self._default_model
        system_prompt = extract_system_prompt(messages, self._default_system)
        bedrock_messages = to_bedrock_messages(messages)

        def _call() -> dict:
            client = self._runtime_client()
            return client.converse(
                modelId=model_id,
                messages=bedrock_messages,
                system=[{"text": system_prompt}],
                inferenceConfig={"temperature": temperature},
            )

        try:
            # boto3 is sync; run it off the event loop.
            response = await asyncio.to_thread(_call)
        except Exception as exc:  # noqa: BLE001 - normalise to ProviderError
            raise ProviderError(f"Bedrock converse failed: {exc}") from exc

        return {
            "text": _extract_text(response),
            "model": model_id,
            "usage": _extract_usage(response),
            "raw": response,
        }

    async def is_reachable(self) -> bool:
        """Best-effort liveness probe used by the auto-fallback factory."""

        def _probe() -> bool:
            client = self.control_plane_client()
            client.list_foundation_models()
            return True

        try:
            return await asyncio.to_thread(_probe)
        except Exception as exc:  # noqa: BLE001
            logger.info("Bedrock not reachable, will fall back to echo: %s", exc)
            return False


# ── response parsing (folded from chatbot/conversation.py) ───────


def _extract_text(response: dict) -> str:
    try:
        blocks = response["output"]["message"]["content"]
        return "".join(b.get("text", "") for b in blocks)
    except (KeyError, IndexError, TypeError):
        return "[no response]"


def _extract_usage(response: dict) -> dict:
    usage = response.get("usage", {}) if isinstance(response, dict) else {}
    return {
        "input_tokens": usage.get("inputTokens", 0),
        "output_tokens": usage.get("outputTokens", 0),
    }
