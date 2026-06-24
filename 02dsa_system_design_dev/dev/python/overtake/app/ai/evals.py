"""Simple eval harness: metrics + a runner.

Offline, dependency-free. Useful for regression-testing the RAG/answer path.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Awaitable, Callable, Sequence

_TOKEN = re.compile(r"\w+")


def keyword_recall(answer: str, expected_keywords: Sequence[str]) -> float:
    """Fraction of expected keywords present in the answer (0..1)."""
    if not expected_keywords:
        return 1.0
    tokens = set(_TOKEN.findall(answer.lower()))
    hits = sum(1 for k in expected_keywords if k.lower() in tokens)
    return hits / len(expected_keywords)


def contains_any(answer: str, options: Sequence[str]) -> bool:
    """True if any option substring appears in the answer (case-insensitive)."""
    low = answer.lower()
    return any(o.lower() in low for o in options)


@dataclass
class EvalCase:
    """A single eval case: a question and the keywords a good answer contains."""

    question: str
    expected_keywords: list[str]


@dataclass
class EvalReport:
    """Aggregate eval results."""

    total: int
    passed: int
    avg_recall: float

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


async def run_evals(
    cases: Sequence[EvalCase],
    answer_fn: Callable[[str], Awaitable[str]],
    *,
    threshold: float = 0.5,
) -> EvalReport:
    """Run each case through `answer_fn` and score keyword recall."""
    recalls: list[float] = []
    passed = 0
    for case in cases:
        answer = await answer_fn(case.question)
        recall = keyword_recall(answer, case.expected_keywords)
        recalls.append(recall)
        if recall >= threshold:
            passed += 1
    avg = sum(recalls) / len(recalls) if recalls else 0.0
    return EvalReport(total=len(cases), passed=passed, avg_recall=avg)
