"""Run the offline eval suite and print a report.

Usage:
    uv run python scripts/run_evals.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make `app` importable when run directly (`python scripts/run_evals.py`); the
# project uses package=false so `app` is not installed into the environment.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ai.models.factory import get_llm_client  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.services.eval_service import EvalService  # noqa: E402


async def main() -> int:
    settings = get_settings()
    service = EvalService(get_llm_client(settings), settings)
    report = await service.run_default_suite()
    print(f"Cases: {len(report.results)}  pass_rate={report.pass_rate:.0%}  mean={report.mean_score:.3f}")
    for r in report.results:
        flag = "PASS" if r.passed else "FAIL"
        print(f"  [{flag}] {r.name}: score={r.score:.3f}")
    return 0 if report.pass_rate >= 0.5 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
