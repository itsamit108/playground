"""Chat use case: orchestrates memory + guardrails + LLM provider.

This is the genuine end-to-end AI path: api/chat -> chat_service -> ai/models.
It folds in the old ``Conversation`` multi-turn history behaviour, now backed
by ``ai/memory.py`` and keyed by session id.
"""

from __future__ import annotations

from app.ai import guardrails
from app.ai.memory import InMemoryConversationMemory, get_default_memory
from app.ai.models.base import LLMClient
from app.ai.prompts.loader import load_prompt
from app.core.config import Settings
from app.schemas.chat import ChatRequest, ChatResponse, Usage


class ChatService:
    def __init__(
        self,
        llm: LLMClient,
        settings: Settings,
        memory: InMemoryConversationMemory | None = None,
    ) -> None:
        self.llm = llm
        self.settings = settings
        self.memory = memory or get_default_memory()

    def _system_prompt(self, override: str | None) -> str:
        if override:
            return override
        try:
            return load_prompt("system")
        except FileNotFoundError:
            return self.settings.system_prompt

    async def chat(self, req: ChatRequest) -> ChatResponse:
        # Input guardrail (raises GuardrailError on injection; redacts PII).
        clean_input = guardrails.check_input(req.message)

        system_prompt = self._system_prompt(req.system_prompt)
        history = self.memory.get(req.session_id)

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": clean_input})

        result = await self.llm.generate(
            messages=messages,
            model=req.model,
            temperature=req.temperature,
        )

        reply = guardrails.check_output(result["text"])

        # Persist turn to memory.
        self.memory.append(req.session_id, {"role": "user", "content": clean_input})
        self.memory.append(req.session_id, {"role": "assistant", "content": reply})

        provider = getattr(self.llm, "name", "unknown")
        usage = result.get("usage", {})
        return ChatResponse(
            reply=reply,
            model=result.get("model", req.model or self.settings.bedrock_model_id),
            provider=provider,
            session_id=req.session_id,
            turn=self.memory.turn_count(req.session_id),
            usage=Usage(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
            ),
        )

    def reset(self, session_id: str) -> None:
        self.memory.reset(session_id)
