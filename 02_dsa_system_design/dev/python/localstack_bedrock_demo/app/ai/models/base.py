"""Model-agnostic LLM contract.

The ``LLMClient`` Protocol is defined verbatim per the 2026 architecture doc.
Every provider (Bedrock, Echo, ...) implements it so the service layer never
depends on a concrete SDK.
"""

from __future__ import annotations

from typing import Any, Protocol, Sequence, TypedDict


class LLMClient(Protocol):
    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict: ...


# ── Typed helpers around the contract ────────────────────────────


class Message(TypedDict):
    """A single chat message in the provider-neutral format.

    ``role`` is "user" | "assistant" | "system"; ``content`` is plain text.
    """

    role: str
    content: str


def to_bedrock_messages(messages: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert provider-neutral messages to Bedrock Converse content blocks.

    System messages are excluded (Bedrock takes them via the ``system`` arg).
    """
    converted: list[dict[str, Any]] = []
    for m in messages:
        if m.get("role") == "system":
            continue
        converted.append(
            {"role": m["role"], "content": [{"text": str(m["content"])}]}
        )
    return converted


def extract_system_prompt(
    messages: Sequence[dict[str, Any]], default: str
) -> str:
    """Return the first system message content, else the default."""
    for m in messages:
        if m.get("role") == "system":
            return str(m["content"])
    return default
