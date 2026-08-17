"""Chat service.

Orchestrates: guardrails -> memory -> LLM provider -> guardrails. The router
never touches the LLM SDK; it calls this service.
"""

from __future__ import annotations

from typing import Any

from app.ai import guardrails
from app.ai.memory import ConversationMemory
from app.ai.models.base import LLMClient, make_message
from app.ai.prompts.loader import load_prompt
from app.core.config import Settings
from app.core.exceptions import GuardrailError


class ChatService:
    """Stateful chat use case backed by an LLMClient and conversation memory."""

    def __init__(
        self,
        llm: LLMClient,
        settings: Settings,
        memory: ConversationMemory | None = None,
    ) -> None:
        self._llm = llm
        self._settings = settings
        self._memory = memory or ConversationMemory()

    async def chat(
        self,
        message: str,
        *,
        session_id: str = "default",
        temperature: float | None = None,
    ) -> dict:
        input_check = guardrails.check_input(message)
        if not input_check.allowed:
            raise GuardrailError(f"Input blocked: {input_check.reason}")
        safe_message = input_check.sanitized or message

        self._memory.add(session_id, "user", safe_message)

        messages: list[dict[str, Any]] = [make_message("system", load_prompt("system"))]
        messages.extend(self._memory.history(session_id))

        result = await self._llm.generate(
            messages,
            model=self._settings.llm_model,
            temperature=(
                temperature if temperature is not None else self._settings.llm_temperature
            ),
        )

        output_check = guardrails.check_output(result["content"])
        reply = output_check.sanitized or result["content"]

        self._memory.add(session_id, "assistant", reply)

        return {
            "reply": reply,
            "provider": result.get("provider", "unknown"),
            "model": result.get("model", self._settings.llm_model),
            "session_id": session_id,
        }
