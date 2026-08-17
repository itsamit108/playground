"""Re-ranking.

A lightweight lexical re-ranker that boosts vector hits by exact keyword
overlap with the query. This nudges the most on-topic chunks to the top after
the embedding recall step. Replace with a cross-encoder reranker in production.
"""

from __future__ import annotations

import re

from app.ai.rag.vector_store import SearchHit

_TOKEN = re.compile(r"\w+")


def rerank(query: str, hits: list[SearchHit], *, top_k: int | None = None) -> list[SearchHit]:
    """Re-order hits by a blend of vector score and lexical overlap."""
    q_terms = {w for w in _TOKEN.findall(query.lower()) if len(w) > 2}

    def combined(hit: SearchHit) -> float:
        h_terms = set(_TOKEN.findall(hit.record.text.lower()))
        overlap = len(q_terms & h_terms)
        lexical = overlap / (len(q_terms) or 1)
        return 0.7 * hit.score + 0.3 * lexical

    ordered = sorted(hits, key=combined, reverse=True)
    return ordered[:top_k] if top_k else ordered
