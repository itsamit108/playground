"""Conversation manager – maintains message history and calls the Converse API."""

from __future__ import annotations

from typing import Any

from chatbot.client import get_bedrock_runtime_client
from chatbot.config import BEDROCK_MODEL_ID, SYSTEM_PROMPT


class Conversation:
    """Stateful multi-turn conversation backed by Bedrock's Converse API."""

    def __init__(
        self,
        model_id: str = BEDROCK_MODEL_ID,
        system_prompt: str = SYSTEM_PROMPT,
    ) -> None:
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.messages: list[dict[str, Any]] = []
        self._client = get_bedrock_runtime_client()

    # ── public API ──────────────────────────────────────────────

    def send(self, user_text: str) -> str:
        """Send a user message and return the assistant's reply."""
        self.messages.append({"role": "user", "content": [{"text": user_text}]})

        response = self._client.converse(
            modelId=self.model_id,
            messages=self.messages,
            system=[{"text": self.system_prompt}],
        )

        assistant_text = self._extract_text(response)
        self.messages.append(
            {"role": "assistant", "content": [{"text": assistant_text}]}
        )
        return assistant_text

    def reset(self) -> None:
        """Clear conversation history."""
        self.messages.clear()

    @property
    def turn_count(self) -> int:
        """Number of user turns so far."""
        return sum(1 for m in self.messages if m["role"] == "user")

    # ── helpers ─────────────────────────────────────────────────

    @staticmethod
    def _extract_text(response: dict) -> str:
        """Pull the text content out of a Converse API response."""
        try:
            output = response["output"]["message"]["content"]
            return "".join(block.get("text", "") for block in output)
        except (KeyError, IndexError, TypeError):
            return "[no response]"
