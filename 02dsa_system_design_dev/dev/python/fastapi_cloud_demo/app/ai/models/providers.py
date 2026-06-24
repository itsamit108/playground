"""Concrete LLM providers implementing the ``LLMClient`` contract.

- ``EchoProvider``: offline, deterministic, zero network. The default.
- ``OllamaProvider``: local Ollama server (no cloud key required).
- ``OpenAICompatProvider``: any OpenAI-compatible chat completions endpoint.

All return the same shape::

    {"content": str, "model": str, "provider": str, "tool_calls": list}
"""

from __future__ import annotations

from typing import Any, Sequence

from app.core.exceptions import ProviderError


def _last_user_text(messages: Sequence[dict[str, Any]]) -> str:
    for message in reversed(list(messages)):
        if message.get("role") == "user":
            return str(message.get("content", ""))
    return ""


class EchoProvider:
    """Deterministic offline provider. Echoes the last user message.

    Useful for development, CI, and as a zero-dependency default. It never
    touches the network, so the whole app runs and tests pass with no keys.
    """

    name = "echo"

    def __init__(self, model: str = "echo-1") -> None:
        self._model = model

    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict:
        user_text = _last_user_text(messages)
        reply = f"Echo: {user_text}" if user_text else "Echo: (no user message)"
        return {
            "content": reply,
            "model": model or self._model,
            "provider": self.name,
            "tool_calls": [],
        }


class OllamaProvider:
    """Local Ollama provider (http://localhost:11434 by default)."""

    name = "ollama"

    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict:
        import httpx  # imported lazily; only needed for this provider

        payload = {
            "model": model or self._model,
            "messages": list(messages),
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(f"{self._base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # pragma: no cover - network path
            raise ProviderError(f"Ollama request failed: {exc}") from exc

        return {
            "content": data.get("message", {}).get("content", ""),
            "model": data.get("model", model or self._model),
            "provider": self.name,
            "tool_calls": [],
        }


class OpenAICompatProvider:
    """Generic OpenAI-compatible chat completions provider."""

    name = "openai"

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model

    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict:
        import httpx  # imported lazily; only needed for this provider

        headers = {"Authorization": f"Bearer {self._api_key}"}
        payload: dict[str, Any] = {
            "model": model or self._model,
            "messages": list(messages),
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # pragma: no cover - network path
            raise ProviderError(f"OpenAI-compatible request failed: {exc}") from exc

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message", {})
        return {
            "content": message.get("content", ""),
            "model": data.get("model", model or self._model),
            "provider": self.name,
            "tool_calls": message.get("tool_calls", []) or [],
        }
