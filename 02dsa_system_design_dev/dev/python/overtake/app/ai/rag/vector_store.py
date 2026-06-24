"""Vector store.

In-memory cosine-similarity store (default, offline). Documents carry arbitrary
metadata (e.g. note_id, owner user_id) so retrieval can be scoped per user.
pgvector / external vector DBs can implement the same `VectorStore` protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence

from app.ai.rag.embeddings import cosine_similarity


@dataclass
class VectorRecord:
    """A stored chunk plus its embedding and metadata."""

    id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    """A retrieval result with a similarity score."""

    record: VectorRecord
    score: float


class VectorStore(Protocol):
    def add(self, record: VectorRecord) -> None: ...
    def search(
        self,
        query_embedding: Sequence[float],
        *,
        top_k: int = 4,
        where: dict[str, Any] | None = None,
    ) -> list[SearchHit]: ...
    def delete_where(self, where: dict[str, Any]) -> int: ...
    def clear(self) -> None: ...


class InMemoryVectorStore:
    """Brute-force in-memory vector store keyed by record id."""

    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    def add(self, record: VectorRecord) -> None:
        self._records[record.id] = record

    @staticmethod
    def _matches(record: VectorRecord, where: dict[str, Any] | None) -> bool:
        if not where:
            return True
        return all(record.metadata.get(k) == v for k, v in where.items())

    def search(
        self,
        query_embedding: Sequence[float],
        *,
        top_k: int = 4,
        where: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        hits = [
            SearchHit(rec, cosine_similarity(query_embedding, rec.embedding))
            for rec in self._records.values()
            if self._matches(rec, where)
        ]
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]

    def delete_where(self, where: dict[str, Any]) -> int:
        to_delete = [
            rid for rid, rec in self._records.items() if self._matches(rec, where)
        ]
        for rid in to_delete:
            del self._records[rid]
        return len(to_delete)

    def clear(self) -> None:
        self._records.clear()

    def __len__(self) -> int:
        return len(self._records)


# Process-wide default store (offline). Services use get_vector_store().
_store = InMemoryVectorStore()


def get_vector_store() -> InMemoryVectorStore:
    """Return the shared in-memory vector store."""
    return _store
