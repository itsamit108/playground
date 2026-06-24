"""Reranker.

A lightweight lexical reranker that boosts results sharing query terms. In
production this is where a cross-encoder / Cohere rerank / LLM reranker fits.
"""

from __future__ import annotations

import re

from app.ai.rag.vector_store import ScoredDocument

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _terms(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def rerank(query: str, results: list[ScoredDocument]) -> list[ScoredDocument]:
    """Re-score results by blending vector score with lexical overlap."""
    query_terms = _terms(query)
    if not query_terms:
        return results

    reranked: list[ScoredDocument] = []
    for item in results:
        overlap = len(query_terms & _terms(item.document.text)) / len(query_terms)
        blended = 0.7 * item.score + 0.3 * overlap
        reranked.append(ScoredDocument(document=item.document, score=blended))
    reranked.sort(key=lambda item: item.score, reverse=True)
    return reranked
