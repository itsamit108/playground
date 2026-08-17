"""Model-agnostic LLM contract.

The ``LLMClient`` Protocol below is the verbatim contract from the 2026
architecture doc. Every provider in ``providers.py`` implements it, which gives
us provider swapping, easy testing, and reduced lock-in.
"""

from __future__ import annotations

from typing import Any, Protocol, Sequence, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    async def generate(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        tools: list | None = None,
    ) -> dict: ...


# --- Typed helpers around the contract ---
def make_message(role: str, content: str) -> dict[str, Any]:
    """Build a single chat message dict in the canonical shape."""
    return {"role": role, "content": content}


def text_of(response: dict[str, Any]) -> str:
    """Extract the assistant text from a provider response dict.

    Providers return at minimum ``{"content": str, ...}``.
    """
    return str(response.get("content", ""))
