"""Simple eval harness — metric + runner.

Deterministic, offline metrics so evals run in CI without keys. The slot for
Pydantic Evals / promptfoo / Langfuse evaluations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Awaitable, Callable

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


# --- Metrics ---
def exact_match(prediction: str, reference: str) -> float:
    return 1.0 if prediction.strip().lower() == reference.strip().lower() else 0.0


def contains(prediction: str, reference: str) -> float:
    return 1.0 if reference.strip().lower() in prediction.lower() else 0.0


def token_f1(prediction: str, reference: str) -> float:
    pred, ref = _tokens(prediction), _tokens(reference)
    if not pred or not ref:
        return 0.0
    overlap = len(pred & ref)
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred)
    recall = overlap / len(ref)
    return 2 * precision * recall / (precision + recall)


@dataclass
class EvalCase:
    name: str
    inputs: dict
    expected: str
    metric: Callable[[str, str], float] = contains


@dataclass
class EvalResult:
    name: str
    score: float
    prediction: str
    expected: str
    passed: bool


@dataclass
class EvalReport:
    results: list[EvalResult]

    @property
    def mean_score(self) -> float:
        return sum(r.score for r in self.results) / len(self.results) if self.results else 0.0

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)


async def run_evals(
    cases: list[EvalCase],
    predict: Callable[[dict], Awaitable[str]],
    *,
    threshold: float = 0.5,
) -> EvalReport:
    """Run each case through ``predict`` and score it. ``predict`` is async."""
    results: list[EvalResult] = []
    for case in cases:
        prediction = await predict(case.inputs)
        score = case.metric(prediction, case.expected)
        results.append(
            EvalResult(
                name=case.name,
                score=score,
                prediction=prediction,
                expected=case.expected,
                passed=score >= threshold,
            )
        )
    return EvalReport(results=results)
