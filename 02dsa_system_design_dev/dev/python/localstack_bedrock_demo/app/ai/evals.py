"""Tiny eval harness: a metric + a runner.

Good fits in production: Pydantic Evals, promptfoo, LangSmith, DSPy. This
offline version scores whether the response contains expected substrings.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass
class EvalCase:
    """A single eval case: prompt + expected substrings."""

    name: str
    prompt: str
    expected_substrings: list[str]


@dataclass
class EvalResult:
    name: str
    passed: bool
    score: float
    output: str


def contains_score(output: str, expected: list[str]) -> float:
    """Fraction of expected substrings present in output (case-insensitive)."""
    if not expected:
        return 1.0
    lowered = output.lower()
    hits = sum(1 for e in expected if e.lower() in lowered)
    return hits / len(expected)


async def run_evals(
    cases: list[EvalCase],
    generate: Callable[[str], Awaitable[str]],
    threshold: float = 1.0,
) -> list[EvalResult]:
    """Run each case through ``generate`` and score it."""
    results: list[EvalResult] = []
    for case in cases:
        output = await generate(case.prompt)
        score = contains_score(output, case.expected_substrings)
        results.append(
            EvalResult(
                name=case.name,
                passed=score >= threshold,
                score=score,
                output=output,
            )
        )
    return results
