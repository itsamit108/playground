"""In-memory vector store.

A tiny cosine-similarity store so RAG runs with zero external services. Swap for
FAISS / Chroma / pgvector / Qdrant etc. behind the same interface in production.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ai.rag.embeddings import HashingEmbedder, cosine_similarity


@dataclass
class Document:
    """A stored document with its embedding."""

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)


@dataclass
class ScoredDocument:
    document: Document
    score: float


class InMemoryVectorStore:
    """Cosine-similarity vector store backed by a Python list."""

    def __init__(self, embedder: HashingEmbedder | None = None) -> None:
        self._embedder = embedder or HashingEmbedder()
        self._docs: list[Document] = []

    def add(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> Document:
        doc = Document(
            id=doc_id,
            text=text,
            metadata=metadata or {},
            embedding=self._embedder.embed(text),
        )
        self._docs.append(doc)
        return doc

    def search(self, query: str, *, top_k: int = 3) -> list[ScoredDocument]:
        query_vec = self._embedder.embed(query)
        scored = [
            ScoredDocument(document=doc, score=cosine_similarity(query_vec, doc.embedding))
            for doc in self._docs
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def __len__(self) -> int:
        return len(self._docs)
