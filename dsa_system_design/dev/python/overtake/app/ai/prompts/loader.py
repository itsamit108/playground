"""Prompt loader: reads .md prompt files from this package directory."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_PROMPT_DIR = Path(__file__).parent


@lru_cache
def load_prompt(name: str) -> str:
    """Load a prompt by file stem (e.g. 'system' -> system.md)."""
    path = _PROMPT_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def system_prompt() -> str:
    """Convenience accessor for the main system prompt."""
    return load_prompt("system")
