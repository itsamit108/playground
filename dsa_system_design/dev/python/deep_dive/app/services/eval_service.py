"""Eval service — runs the chat path against a small offline eval suite."""

from __future__ import annotations

from app.ai.evals import EvalCase, EvalReport, contains, run_evals
from app.ai.models.base import LLMClient, make_message
from app.core.config import Settings


def default_cases() -> list[EvalCase]:
    return [
        EvalCase(
            name="echo_roundtrip",
            inputs={"text": "hello world"},
            expected="hello world",
            metric=contains,
        ),
        EvalCase(
            name="greeting",
            inputs={"text": "say something about books"},
            expected="books",
            metric=contains,
        ),
    ]


class EvalService:
    def __init__(self, llm: LLMClient, settings: Settings):
        self.llm = llm
        self.settings = settings

    async def run_default_suite(self) -> EvalReport:
        async def predict(inputs: dict) -> str:
            resp = await self.llm.generate([make_message("user", str(inputs["text"]))])
            return str(resp.get("content", ""))

        return await run_evals(default_cases(), predict, threshold=0.5)
