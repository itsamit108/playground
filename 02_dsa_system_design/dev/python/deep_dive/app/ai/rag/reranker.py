"""Re-ranking of retrieved hits.

Offline default: a lightweight lexical-overlap reranker that nudges results
whose terms overlap the query, blended with the original vector score. The slot
for a cross-encoder / Cohere / LLM reranker.
"""

from __future__ import annotations

import re

from app.ai.rag.vector_store import SearchHit

_WORD_RE = re.compile(r"[a-z0-9]+")


def _terms(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def rerank(query: str, hits: list[SearchHit], *, top_k: int | None = None) -> list[SearchHit]:
    q_terms = _terms(query)
    if not q_terms:
        return hits[: top_k or len(hits)]

    rescored: list[SearchHit] = []
    for hit in hits:
        overlap = len(q_terms & _terms(hit.text)) / len(q_terms)
        blended = 0.7 * hit.score + 0.3 * overlap
        rescored.append(
            SearchHit(text=hit.text, source=hit.source, score=blended, metadata=hit.metadata)
        )
    rescored.sort(key=lambda h: h.score, reverse=True)
    return rescored[: top_k or len(rescored)]
