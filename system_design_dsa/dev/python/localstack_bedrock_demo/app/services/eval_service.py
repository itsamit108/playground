"""Eval use case: run the offline eval harness against the chat path."""

from __future__ import annotations

from app.ai.evals import EvalCase, EvalResult, run_evals
from app.ai.models.base import LLMClient


class EvalService:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def run_default_suite(self) -> list[EvalResult]:
        cases = [
            EvalCase(
                name="echo_smoke",
                prompt="hello world",
                expected_substrings=["hello"],
            ),
        ]

        async def _generate(prompt: str) -> str:
            result = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}]
            )
            return result["text"]

        return await run_evals(cases, _generate, threshold=1.0)
