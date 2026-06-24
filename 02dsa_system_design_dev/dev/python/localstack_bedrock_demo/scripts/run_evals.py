"""Run the offline eval suite (runnable).

Usage:
    uv run python -m scripts.run_evals
"""

from __future__ import annotations

import asyncio

from app.ai.models.factory import get_offline_client
from app.core.config import get_settings
from app.services.eval_service import EvalService


async def _run() -> int:
    settings = get_settings()
    llm = get_offline_client(settings)
    results = await EvalService(llm).run_default_suite()
    failures = 0
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        if not r.passed:
            failures += 1
        print(f"[{status}] {r.name} score={r.score:.2f} output={r.output!r}")
    print(f"\n{len(results) - failures}/{len(results)} passed")
    return 1 if failures else 0


def main() -> None:
    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
