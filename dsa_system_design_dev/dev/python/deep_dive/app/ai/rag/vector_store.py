"""In-memory vector store (offline default).

A thread-safe, process-local store with cosine search. This is the slot for a
real vector DB (Chroma, Qdrant, pgvector, Pinecone, ...) behind the same
interface.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from app.ai.rag.embeddings import cosine_similarity


@dataclass
class StoredItem:
    text: str
    source: str
    embedding: list[float]
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class SearchHit:
    text: str
    source: str
    score: float
    metadata: dict[str, str] = field(default_factory=dict)


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._items: list[StoredItem] = []
        self._lock = threading.Lock()

    def add(
        self,
        text: str,
        embedding: list[float],
        *,
        source: str = "inline",
        metadata: dict[str, str] | None = None,
    ) -> None:
        with self._lock:
            self._items.append(
                StoredItem(text=text, source=source, embedding=embedding, metadata=metadata or {})
            )

    def add_many(self, items: list[StoredItem]) -> None:
        with self._lock:
            self._items.extend(items)

    def search(self, query_embedding: list[float], top_k: int = 4) -> list[SearchHit]:
        with self._lock:
            items = list(self._items)
        scored = [
            SearchHit(
                text=it.text,
                source=it.source,
                score=cosine_similarity(query_embedding, it.embedding),
                metadata=it.metadata,
            )
            for it in items
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        with self._lock:
            return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
