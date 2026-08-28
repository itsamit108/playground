"""Embeddings.

A deterministic, offline hashing-bag-of-words embedder so RAG works with zero
external services or API keys. Swap for a real embedding model (OpenAI, Ollama,
sentence-transformers) by implementing the same ``embed`` interface.
"""

from __future__ import annotations

import hashlib
import math
import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_DIM = 256


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _stable_hash(token: str) -> int:
    """Process-independent hash (unlike built-in ``hash`` for str)."""
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")


class HashingEmbedder:
    """Deterministic hashing embedder producing L2-normalized vectors."""

    def __init__(self, dim: int = _DIM) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _tokenize(text):
            vec[_stable_hash(token) % self.dim] += 1.0
        norm = math.sqrt(sum(value * value for value in vec))
        if norm == 0:
            return vec
        return [value / norm for value in vec]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity of two equal-length vectors."""
    return sum(x * y for x, y in zip(a, b))
