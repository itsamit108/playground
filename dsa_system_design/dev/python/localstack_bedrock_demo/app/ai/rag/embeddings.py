"""Embeddings.

Offline, deterministic hashing-bag-of-words embedder so RAG works with no
external embedding service. Swap for Bedrock Titan / OpenAI / local models in
production by implementing the same ``embed`` signature.
"""

from __future__ import annotations

import math
import re

_TOKEN = re.compile(r"[a-z0-9]+")


class HashingEmbedder:
    """Deterministic hashing embedder producing fixed-size L2-normalised vectors."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in _TOKEN.findall(text.lower()):
            vec[hash(tok) % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0:
            return vec
        return [v / norm for v in vec]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]
