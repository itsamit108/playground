"""Built-in function tools.

`search_notes` is a real tool: it runs the RAG retriever over the current
user's notes and returns matching snippets. The agent uses it to ground its
answers. The tool is registered at import time into the shared registry.
"""

from __future__ import annotations

from typing import Any

from app.ai.rag.retriever import Retriever
from app.ai.tools.registry import Tool, _raw_registry


def search_notes(*, user_id: int, query: str, top_k: int = 4) -> list[dict[str, Any]]:
    """Semantic search over a user's notes. Returns snippet dicts."""
    retriever = Retriever()
    chunks = retriever.retrieve(user_id=user_id, query=query, top_k=top_k)
    return [
        {
            "note_id": c.note_id,
            "note_title": c.note_title,
            "snippet": c.text,
            "score": round(c.score, 4),
        }
        for c in chunks
    ]


def word_count(*, text: str) -> dict[str, int]:
    """Count words and characters in a piece of text."""
    words = len(text.split())
    return {"words": words, "characters": len(text)}


# ── Register tools at import time ───────────────────────────────────────────
_raw_registry().register(
    Tool(
        name="search_notes",
        description="Semantic search over the current user's notes.",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "Owner user id"},
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "description": "Max results"},
            },
            "required": ["user_id", "query"],
        },
        func=search_notes,
    )
)

_raw_registry().register(
    Tool(
        name="word_count",
        description="Count words and characters in text.",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        func=word_count,
    )
)
