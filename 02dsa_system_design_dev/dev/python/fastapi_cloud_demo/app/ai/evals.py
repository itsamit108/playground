"""Simple eval harness: a metric + a runner.

Framework-agnostic. This is where Pydantic Evals / DSPy / promptfoo / Langfuse
evaluations would plug in for production-grade evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Sequence


@dataclass
class EvalCase:
    """A single eval case: an input and an expected substring."""

    name: str
    prompt: str
    expected_substring: str


@dataclass
class EvalResult:
    name: str
    passed: bool
    output: str


def contains_metric(output: str, expected_substring: str) -> bool:
    """Metric: case-insensitive substring containment."""
    return expected_substring.lower() in output.lower()


async def run_evals(
    cases: Sequence[EvalCase],
    generate: Callable[[str], Awaitable[str]],
) -> list[EvalResult]:
    """Run each case through ``generate`` and score with ``contains_metric``."""
    results: list[EvalResult] = []
    for case in cases:
        output = await generate(case.prompt)
        results.append(
            EvalResult(
                name=case.name,
                passed=contains_metric(output, case.expected_substring),
                output=output,
            )
        )
    return results


# A default suite usable with the EchoProvider (which echoes the input).
DEFAULT_SUITE: list[EvalCase] = [
    EvalCase(name="echo_hello", prompt="hello world", expected_substring="hello world"),
    EvalCase(name="echo_specs", prompt="system specs please", expected_substring="specs"),
]
