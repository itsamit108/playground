"""Built-in function tools."""

from __future__ import annotations

import re

from app.ai.tools.registry import Tool, ToolRegistry


def word_count(text: str) -> dict[str, int]:
    """Count words and characters in text."""
    words = re.findall(r"\S+", text)
    return {"words": len(words), "characters": len(text)}


def slugify(text: str) -> dict[str, str]:
    """Convert text to a URL/file-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return {"slug": slug or "untitled"}


def register_builtins(registry: ToolRegistry) -> None:
    registry.register(
        Tool(
            name="word_count",
            description="Count the words and characters in a piece of text.",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            handler=word_count,
        )
    )
    registry.register(
        Tool(
            name="slugify",
            description="Convert text into a URL/file-safe slug.",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            handler=slugify,
        )
    )
