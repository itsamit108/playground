"""Eval-suite test: the RAG/chat path passes a keyword-recall eval offline."""

from __future__ import annotations

import asyncio

from app.ai.evals import EvalCase
from app.core.security import hash_password
from app.infra.db import Note, User
from app.services import eval_service


def test_chat_eval_passes(session):
    user = User(
        username="evaluser",
        email="eval@example.com",
        hashed_password=hash_password("password123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    for title, content in [
        ("Grocery list", "Buy milk, eggs, spinach, and basil."),
        ("Project Apollo", "Apollo launch is scheduled for Q3."),
        ("Workout plan", "Friday is a 5k running day."),
    ]:
        session.add(Note(title=title, content=content, user_id=user.id))
    session.commit()

    cases = [
        EvalCase("When is the Apollo launch?", ["q3"]),
        EvalCase("What should I buy at the store?", ["milk", "eggs"]),
        EvalCase("What is my Friday workout?", ["running"]),
    ]
    report = asyncio.run(eval_service.evaluate_chat(session, user, cases, threshold=0.4))
    assert report.total == 3
    assert report.pass_rate >= 0.6
