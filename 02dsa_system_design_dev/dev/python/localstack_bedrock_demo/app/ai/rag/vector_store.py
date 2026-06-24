"""In-memory vector store with cosine similarity search.

Pluggable: replace with FAISS / pgvector / Qdrant / OpenSearch in production
behind the same interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Document:
    id: str
    text: str
    embedding: list[float]
    metadata: dict = field(default_factory=dict)


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity for (assumed L2-normalised) vectors."""
    return sum(x * y for x, y in zip(a, b))


class InMemoryVectorStore:
    """Simple list-backed vector store."""

    def __init__(self) -> None:
        self._docs: list[Document] = []

    def add(self, doc: Document) -> None:
        self._docs.append(doc)

    def clear(self) -> None:
        self._docs.clear()

    def __len__(self) -> int:
        return len(self._docs)

    def search(self, query_embedding: list[float], k: int = 3) -> list[tuple[Document, float]]:
        scored = [(d, cosine(query_embedding, d.embedding)) for d in self._docs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]
