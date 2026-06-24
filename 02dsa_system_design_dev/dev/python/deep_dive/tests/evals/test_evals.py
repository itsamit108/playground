"""Eval-suite tests (offline)."""

from __future__ import annotations

import pytest

from app.ai.evals import contains, exact_match, token_f1
from app.ai.models.providers import EchoProvider
from app.services.eval_service import EvalService


def test_metrics():
    assert exact_match("Yes", "yes") == 1.0
    assert contains("the answer is books", "books") == 1.0
    assert token_f1("the quick brown fox", "quick brown") > 0.0


@pytest.mark.asyncio
async def test_eval_service_runs_default_suite(settings):
    service = EvalService(EchoProvider(), settings)
    report = await service.run_default_suite()
    assert report.results
    # EchoProvider echoes the input, so 'contains' cases should pass.
    assert report.pass_rate >= 0.5
