"""Embeddings.

Offline-first deterministic embedder: a hashing bag-of-words projected into a
fixed-dimension vector, L2-normalized. No model download, no network — yet it
yields meaningful cosine similarity for retrieval and is fully reproducible.

This is the integration point for real embedding backends (Gemini embeddings,
OpenAI, sentence-transformers, LlamaIndex/Haystack embedders).
"""

from __future__ import annotations

import math
import re
from typing import Protocol

_WORD_RE = re.compile(r"[a-z0-9]+")


class Embedder(Protocol):
    @property
    def dim(self) -> int: ...

    def embed(self, text: str) -> list[float]: ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class HashingEmbedder:
    """Deterministic hashing embedder (offline default)."""

    def __init__(self, dim: int = 256):
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self._dim
        tokens = _WORD_RE.findall(text.lower())
        for tok in tokens:
            h = hash((tok, "deepdive-embed")) % self._dim
            sign = 1.0 if (hash(tok) >> 1) % 2 == 0 else -1.0
            vec[h] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity of two equal-length vectors (assumes finite values)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
