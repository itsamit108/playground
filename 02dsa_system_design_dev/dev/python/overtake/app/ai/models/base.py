"""Model-agnostic LLM contract.

The `LLMClient` Protocol is defined verbatim per the 2026 architecture doc.
Typed helpers (`Message`, `Role`) are layered on top for convenience without
changing the contract.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol, Sequence, TypedDict


class LLMClient(Protocol):
    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict:
        ...


# ── Typed helpers (optional sugar around the dict-based contract) ────────────
Role = Literal["system", "user", "assistant", "tool"]


class Message(TypedDict):
    """A single chat message as passed to `LLMClient.generate`."""

    role: Role
    content: str


def msg(role: Role, content: str) -> Message:
    """Build a chat message dict."""
    return {"role": role, "content": content}
