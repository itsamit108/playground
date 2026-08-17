"""Eval service.

Runs the ai/evals harness against the configured chat path. Used by the
``scripts/run_evals.py`` runner and the evals tests.
"""

from __future__ import annotations

from app.ai.evals import DEFAULT_SUITE, EvalCase, EvalResult, run_evals
from app.ai.models.base import LLMClient, make_message


class EvalService:
    """Runs eval suites through an LLMClient."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def run(self, cases: list[EvalCase] | None = None) -> list[EvalResult]:
        suite = cases if cases is not None else DEFAULT_SUITE

        async def generate(prompt: str) -> str:
            result = await self._llm.generate([make_message("user", prompt)])
            return result["content"]

        return await run_evals(suite, generate)
