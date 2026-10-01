"""Model-agnostic LLM contract.

The ``LLMClient`` Protocol is the single contract every provider implements.
It is intentionally provider-neutral: messages in, a dict out.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol, Sequence, TypedDict, runtime_checkable


# --- Typed helpers around the contract ---

Role = Literal["system", "user", "assistant", "tool"]


class Message(TypedDict):
    """A single chat message."""

    role: Role
    content: str


def make_message(role: Role, content: str) -> dict[str, Any]:
    """Construct a chat message dict (compatible with ``LLMClient.generate``)."""
    return {"role": role, "content": content}


# --- The contract (verbatim from the architecture doc) ---


@runtime_checkable
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
