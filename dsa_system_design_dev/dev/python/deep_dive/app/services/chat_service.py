"""Chat service — orchestrates guardrails, memory, optional RAG, and the LLM.

Demonstrates the canonical dependency direction:
``api/chat.py -> services/chat_service.py -> ai/models/*`` (and ai/rag, ai/memory,
ai/guardrails). The router never imports an LLM SDK.
"""

from __future__ import annotations

import uuid

from app.ai import guardrails
from app.ai.memory import get_memory
from app.ai.models.base import LLMClient, make_message
from app.ai.prompts.loader import load_prompt
from app.core.config import Settings
from app.core.exceptions import GuardrailError
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.retrieval_service import RetrievalService


class ChatService:
    def __init__(self, llm: LLMClient, settings: Settings):
        self.llm = llm
        self.settings = settings
        self.memory = get_memory()

    async def chat(self, req: ChatRequest) -> ChatResponse:
        last_user = next(
            (m.content for m in reversed(req.messages) if m.role == "user"), ""
        )

        # Inbound guardrail.
        gin = guardrails.check_input(last_user)
        if not gin.allowed:
            raise GuardrailError(f"Input blocked: {', '.join(gin.findings)}")

        session_id = req.session_id or str(uuid.uuid4())
        sources: list[str] = []

        # Build message list, starting from system prompt.
        messages: list[dict] = [make_message("system", load_prompt("system"))]

        # Optional RAG grounding.
        if req.use_rag:
            retrieval = RetrievalService(self.settings)
            results = retrieval.retrieve(last_user, top_k=self.settings.rag_top_k)
            if results.results:
                context = "\n\n".join(
                    f"[{r.source}] {r.text}" for r in results.results
                )
                sources = list(dict.fromkeys(r.source for r in results.results))
                messages.append(
                    make_message("system", f"Relevant context:\n{context}")
                )

        # Prior session memory + this turn's messages.
        messages.extend(self.memory.get(session_id))
        for m in req.messages:
            messages.append(make_message(m.role, m.content))

        resp = await self.llm.generate(
            messages,
            model=req.model or self.settings.llm_model,
            temperature=req.temperature,
        )
        content = str(resp.get("content", ""))

        # Outbound guardrail (redact PII if any).
        gout = guardrails.check_output(content)
        content = gout.sanitized or content

        # Persist this turn to memory.
        self.memory.append(session_id, make_message("user", last_user))
        self.memory.append(session_id, make_message("assistant", content))

        return ChatResponse(
            content=content,
            model=str(resp.get("model", self.settings.llm_model)),
            provider=str(resp.get("provider", "unknown")),
            session_id=session_id,
            sources=sources,
        )
