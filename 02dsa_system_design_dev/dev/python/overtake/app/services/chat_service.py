"""Chat service: RAG over the user's notes (retrieve -> ground -> generate).

Pulls relevant note chunks, injects them as grounding context into the system
prompt, runs the LLM (EchoProvider by default), and applies guardrails to both
input and output. Conversation memory is updated per session.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session

from app.ai import guardrails
from app.ai.memory import get_memory
from app.ai.models.base import LLMClient, msg
from app.ai.models.factory import get_llm_client
from app.ai.prompts.loader import system_prompt
from app.ai.rag.retriever import RetrievedChunk
from app.core.config import Settings, get_settings
from app.core.exceptions import GuardrailError
from app.infra.db import User
from app.infra.observability import span
from app.services import retrieval_service


@dataclass
class ChatResult:
    answer: str
    citations: list[RetrievedChunk]
    model: str
    session_id: str | None


async def ask(
    session: Session,
    user: User,
    *,
    message: str,
    session_id: str | None = None,
    top_k: int | None = None,
    llm: LLMClient | None = None,
    settings: Settings | None = None,
) -> ChatResult:
    """Answer a question grounded in the user's notes."""
    settings = settings or get_settings()
    llm = llm or get_llm_client(settings)
    memory = get_memory()

    # ── Input guardrail ──────────────────────────────────────────────────
    in_check = guardrails.check_input(message)
    if not in_check.ok:
        raise GuardrailError(f"Input rejected: {in_check.reason}")
    clean_message = in_check.text

    with span("chat.retrieve", user_id=user.id):
        chunks = retrieval_service.search(
            session, user, query=clean_message, top_k=top_k
        )

    if chunks:
        context = "\n".join(
            f"- ({c.note_title}) {c.text}" for c in chunks
        )
        system = f"{system_prompt()}\n\nContext:\n{context}"
    else:
        system = (
            f"{system_prompt()}\n\nContext:\n(no matching notes were found)"
        )

    messages = [msg("system", system)]
    if session_id:
        messages.extend(memory.history(session_id))
    messages.append(msg("user", clean_message))

    with span("chat.generate", model=settings.llm_model):
        out = await llm.generate(
            messages, model=settings.llm_model, temperature=settings.llm_temperature
        )
    answer = out.get("content", "")

    # ── Output guardrail ─────────────────────────────────────────────────
    out_check = guardrails.check_output(answer)
    answer = out_check.text if out_check.ok else "I cannot provide that answer."

    if session_id:
        memory.append(session_id, "user", clean_message)
        memory.append(session_id, "assistant", answer)

    return ChatResult(
        answer=answer,
        citations=chunks,
        model=str(out.get("model", settings.llm_model)),
        session_id=session_id,
    )
