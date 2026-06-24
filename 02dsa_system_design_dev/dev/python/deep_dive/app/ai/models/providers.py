"""Concrete LLM providers implementing the ``LLMClient`` contract.

* ``EchoProvider`` — deterministic, zero-network. Default when no key is set.
* ``GeminiProvider`` — wraps ``google-genai``; supports plain text generation and
  multimodal (image) generation for the PDF -> EPUB pipeline. Gracefully reports
  itself unavailable when the SDK or an API key is missing.
"""

from __future__ import annotations

import asyncio
from typing import Any, Sequence

from app.core.exceptions import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _join_messages(messages: Sequence[dict[str, Any]]) -> tuple[str, str]:
    """Return (system_text, user_text) collapsed from a message list."""
    system_parts: list[str] = []
    convo_parts: list[str] = []
    for m in messages:
        role = m.get("role", "user")
        content = str(m.get("content", ""))
        if role == "system":
            system_parts.append(content)
        else:
            convo_parts.append(f"{role}: {content}")
    return "\n".join(system_parts), "\n".join(convo_parts)


class EchoProvider:
    """Deterministic offline provider. No network, no keys.

    It produces a readable, structured echo of the conversation so that the
    entire app — including the PDF->EPUB agent workflow — runs end-to-end with
    zero external services. When asked to produce XHTML (the EPUB use case) it
    returns valid, well-formed XHTML so downstream EPUB assembly succeeds.
    """

    name = "echo"

    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict:
        system_text, user_text = _join_messages(messages)
        wants_xhtml = "xhtml" in system_text.lower() or "epub" in system_text.lower()

        if wants_xhtml:
            content = self._echo_xhtml(user_text)
        else:
            last_user = next(
                (m["content"] for m in reversed(messages) if m.get("role") == "user"),
                user_text,
            )
            content = f"[echo] {last_user}".strip()

        return {
            "content": content,
            "model": model or "echo-1",
            "provider": self.name,
            "usage": {"prompt_chars": len(user_text), "completion_chars": len(content)},
        }

    @staticmethod
    def _echo_xhtml(source_text: str) -> str:
        """Produce a minimal but well-formed XHTML body fragment for EPUB output."""
        import html

        snippet = html.escape(source_text.strip()) or "(no extracted text)"
        # Keep it compact; downstream validator wraps and parses this.
        paragraphs = "\n".join(
            f"  <p>{html.escape(line.strip())}</p>"
            for line in source_text.splitlines()
            if line.strip()
        ) or f"  <p>{snippet}</p>"
        return f"<h1>Converted Content</h1>\n{paragraphs}"


class GeminiProvider:
    """Google Gemini provider via ``google-genai``.

    Implements ``LLMClient.generate`` for chat, and exposes
    ``generate_multimodal`` for the image-aware EPUB content generation that the
    original app relied on.
    """

    name = "gemini"

    def __init__(self, api_key: str, default_model: str = "gemini-3.1-flash-lite"):
        if not api_key:
            raise ProviderError("GeminiProvider requires an API key.")
        try:
            from google import genai  # noqa: F401
        except ImportError as exc:  # pragma: no cover - depends on env
            raise ProviderError(f"google-genai not installed: {exc}") from exc
        from google import genai

        self._genai = genai
        self._client = genai.Client(api_key=api_key)
        self._default_model = default_model

    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict:
        from google.genai import types

        system_text, _ = _join_messages(messages)
        # Build Gemini contents from the conversation (excluding system).
        contents = []
        for m in messages:
            if m.get("role") == "system":
                continue
            role = "model" if m.get("role") == "assistant" else "user"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=str(m.get("content", "")))])
            )

        config = types.GenerateContentConfig(
            system_instruction=system_text or None,
            temperature=temperature,
        )

        def _call() -> str:
            resp = self._client.models.generate_content(
                model=model or self._default_model,
                contents=contents,
                config=config,
            )
            return resp.text or ""

        try:
            text = await asyncio.to_thread(_call)
        except Exception as exc:  # pragma: no cover - network path
            raise ProviderError(f"Gemini generation failed: {exc}") from exc

        return {
            "content": text,
            "model": model or self._default_model,
            "provider": self.name,
            "usage": {},
        }

    async def generate_multimodal(
        self,
        *,
        text: str,
        image_bytes: list[bytes],
        system_instruction: str,
        model: str | None = None,
        temperature: float = 0.1,
        max_output_tokens: int = 65536,
    ) -> str:
        """Text + images -> text. Used by the EPUB content generator."""
        from google.genai import types

        parts: list[Any] = [types.Part.from_text(text=text)]
        for img in image_bytes:
            parts.append(types.Part.from_bytes(data=img, mime_type="image/jpeg"))

        def _call() -> str:
            resp = self._client.models.generate_content(
                model=model or self._default_model,
                contents=[types.Content(role="user", parts=parts)],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )
            return resp.text or ""

        try:
            return await asyncio.to_thread(_call)
        except Exception as exc:  # pragma: no cover - network path
            raise ProviderError(f"Gemini multimodal generation failed: {exc}") from exc
