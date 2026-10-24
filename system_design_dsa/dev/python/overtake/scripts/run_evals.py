"""Run the offline eval harness against the chat path with seeded notes.

Usage:
    uv run python -m scripts.run_evals

Uses an in-memory SQLite DB + a seeded user/notes so it needs no external
services and no API keys (EchoProvider).
"""

from __future__ import annotations

import asyncio

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.ai.evals import EvalCase
from app.ai.rag.vector_store import get_vector_store
from app.core.security import hash_password
from app.infra.db import Note, User, set_engine
from app.services import eval_service


SEED_NOTES = [
    ("Grocery list", "Buy milk, eggs, spinach, and fresh basil for pesto."),
    ("Project Apollo", "Apollo launch is scheduled for Q3. Owner is Priya."),
    ("Workout plan", "Monday squats, Wednesday deadlifts, Friday running 5k."),
]

CASES = [
    EvalCase("When is the Apollo launch?", ["q3"]),
    EvalCase("What should I buy at the store?", ["milk", "eggs"]),
    EvalCase("What is my Friday workout?", ["running"]),
]


async def _amain() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    set_engine(engine)
    SQLModel.metadata.create_all(engine)
    get_vector_store().clear()

    with Session(engine) as session:
        user = User(
            username="seed", email="seed@example.com",
            hashed_password=hash_password("password"),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        for title, content in SEED_NOTES:
            session.add(Note(title=title, content=content, user_id=user.id))
        session.commit()

        report = await eval_service.evaluate_chat(session, user, CASES)

    print(
        f"Evals: {report.passed}/{report.total} passed "
        f"(avg recall {report.avg_recall:.2f}, pass rate {report.pass_rate:.0%})"
    )


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
