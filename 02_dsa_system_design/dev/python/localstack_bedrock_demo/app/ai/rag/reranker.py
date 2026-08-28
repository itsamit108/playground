"""Re-ranking of retrieved candidates.

Offline lexical re-ranker that boosts candidates sharing query terms. Swap for
a cross-encoder / Cohere / Bedrock rerank model in production.
"""

from __future__ import annotations

import re

_TOKEN = re.compile(r"[a-z0-9]+")


def _terms(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


def rerank(
    query: str, candidates: list[tuple[str, float]], top_k: int = 3
) -> list[tuple[str, float]]:
    """Re-rank (text, score) candidates by blending vector score + term overlap."""
    q_terms = _terms(query)

    def blended(item: tuple[str, float]) -> float:
        text, score = item
        if not q_terms:
            return score
        overlap = len(q_terms & _terms(text)) / len(q_terms)
        return 0.7 * score + 0.3 * overlap

    ranked = sorted(candidates, key=blended, reverse=True)
    return ranked[:top_k]
