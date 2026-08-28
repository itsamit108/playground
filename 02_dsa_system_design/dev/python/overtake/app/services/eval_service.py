"""Eval service: run the offline eval harness against the chat path.

Wraps `app.ai.evals` so callers (scripts/tests) get a one-call entry point.
"""

from __future__ import annotations

from sqlmodel import Session

from app.ai.evals import EvalCase, EvalReport, run_evals
from app.infra.db import User
from app.services import chat_service


async def evaluate_chat(
    session: Session,
    user: User,
    cases: list[EvalCase],
    *,
    threshold: float = 0.4,
) -> EvalReport:
    """Run eval cases through the chat service and score keyword recall."""

    async def answer_fn(question: str) -> str:
        result = await chat_service.ask(session, user, message=question)
        return result.answer

    return await run_evals(cases, answer_fn, threshold=threshold)
