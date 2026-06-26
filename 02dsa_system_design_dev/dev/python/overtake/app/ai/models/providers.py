"""Concrete LLM providers implementing the `LLMClient` contract.

`EchoProvider` is the offline, deterministic default: it needs no network and
no API keys, yet produces *grounded, sensible* answers by reading any context
the caller injects into the message list. This keeps the AI feature genuinely
useful in tests and local runs.

`OpenAIProvider` / `AnthropicProvider` are thin extension points that only
import their SDKs lazily, so the package imports cleanly without them.
"""

from __future__ import annotations

import re
from typing import Any, Sequence

from app.ai.models.base import LLMClient


def _last_user_message(messages: Sequence[dict[str, Any]]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return str(m.get("content", ""))
    return ""


def _system_context(messages: Sequence[dict[str, Any]]) -> str:
    """Concatenate system messages (where RAG context is injected)."""
    return "\n".join(
        str(m.get("content", "")) for m in messages if m.get("role") == "system"
    )


def _extract_context_block(system_text: str) -> str:
    """Pull the text after a 'Context:' marker, if present."""
    marker = "Context:"
    idx = system_text.find(marker)
    if idx == -1:
        return ""
    return system_text[idx + len(marker):].strip()


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


class EchoProvider:
    """Deterministic, offline provider.

    Strategy:
    - If grounding context is present, answer extractively: return the context
      sentences most relevant to the question (keyword overlap). This makes the
      RAG path produce real, grounded answers with zero dependencies.
    - Otherwise, echo a deterministic acknowledgement of the user's question.
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
        question = _last_user_message(messages)
        context = _extract_context_block(_system_context(messages))

        if context:
            answer = self._answer_from_context(question, context)
        else:
            answer = f"You asked: {question.strip()}"

        return {
            "content": answer,
            "model": model or "echo-1",
            "role": "assistant",
            "tool_calls": [],
            "finish_reason": "stop",
        }

    @staticmethod
    def _answer_from_context(question: str, context: str) -> str:
        q_terms = {w for w in re.findall(r"\w+", question.lower()) if len(w) > 2}
        sentences = [s.strip() for s in _SENTENCE_SPLIT.split(context) if s.strip()]
        if not sentences:
            return "I could not find anything relevant in your notes."

        scored: list[tuple[int, int, str]] = []
        for i, s in enumerate(sentences):
            s_terms = set(re.findall(r"\w+", s.lower()))
            overlap = len(q_terms & s_terms)
            scored.append((overlap, -i, s))

        scored.sort(reverse=True)
        top = [s for score, _, s in scored if score > 0][:3]
        if not top:
            # No keyword overlap: fall back to the first lines of context.
            top = sentences[:2]

        body = " ".join(top)
        return f"Based on your notes: {body}"


class OpenAIProvider:
    """OpenAI-backed provider (extension point; SDK imported lazily)."""

    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
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
        # Optional extra (not a declared dependency); imported lazily.
        from openai import AsyncOpenAI  # ty: ignore[unresolved-import]

        client = AsyncOpenAI(api_key=self._api_key)
        resp = await client.chat.completions.create(
            model=model or self._model,
            messages=list(messages),
            temperature=temperature,
            tools=tools or None,
        )
        choice = resp.choices[0]
        return {
            "content": choice.message.content or "",
            "model": resp.model,
            "role": "assistant",
            "tool_calls": choice.message.tool_calls or [],
            "finish_reason": choice.finish_reason,
        }


class AnthropicProvider:
    """Anthropic Claude-backed provider (extension point; SDK imported lazily)."""

    name = "anthropic"

    def __init__(self, api_key: str, model: str) -> None:
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
        # Optional extra (not a declared dependency); imported lazily.
        from anthropic import AsyncAnthropic  # ty: ignore[unresolved-import]

        client = AsyncAnthropic(api_key=self._api_key)
        system = _system_context(messages)
        chat = [m for m in messages if m.get("role") != "system"]
        resp = await client.messages.create(
            model=model or self._model,
            system=system or None,
            messages=list(chat),  # type: ignore[arg-type]
            max_tokens=1024,
            temperature=temperature,
        )
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )
        return {
            "content": text,
            "model": resp.model,
            "role": "assistant",
            "tool_calls": [],
            "finish_reason": resp.stop_reason,
        }


# Static check: the providers satisfy the LLMClient protocol.
_check: LLMClient = EchoProvider()
