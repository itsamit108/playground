"""Embeddings.

A deterministic, offline, dependency-free hashing embedder (the "hashing
trick"): each token is hashed into a fixed-width vector dimension and the
vector is L2-normalised. No model download, no API key, fully reproducible —
ideal for tests and local RAG. Swap for a real embedding model (OpenAI,
sentence-transformers, etc.) behind the same `Embedder` protocol in production.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, Sequence

_TOKEN = re.compile(r"\w+")


class Embedder(Protocol):
    dim: int

    def embed(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]: ...


class HashingEmbedder:
    """Deterministic bag-of-words hashing embedder with L2 normalisation."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _bucket(self, token: str) -> int:
        h = hashlib.md5(token.encode("utf-8")).digest()
        return int.from_bytes(h[:4], "big") % self.dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in _TOKEN.findall(text.lower()):
            vec[self._bucket(tok)] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity of two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
