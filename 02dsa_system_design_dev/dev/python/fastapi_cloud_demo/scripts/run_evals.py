"""Run the offline eval suite against the chat path and print a report.

Usage:
    uv run python scripts/run_evals.py

Uses the configured provider (offline EchoProvider by default) so it needs no
external services and no API keys.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make `app` importable when run directly; the project is not installed.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ai.models.factory import get_llm_client  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.services.eval_service import EvalService  # noqa: E402


async def main() -> int:
    settings = get_settings()
    service = EvalService(get_llm_client(settings))
    results = await service.run()

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    rate = (passed / total) if total else 0.0
    print(f"Cases: {total}  passed={passed}  pass_rate={rate:.0%}")
    for r in results:
        flag = "PASS" if r.passed else "FAIL"
        print(f"  [{flag}] {r.name}: {r.output[:80]!r}")
    return 0 if total and passed == total else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
