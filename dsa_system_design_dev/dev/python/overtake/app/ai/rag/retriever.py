"""Retriever: ties chunking + embeddings + vector store + reranking together.

This is the RAG pipeline entry point used by services. It indexes a user's
notes into the vector store (scoped by user_id metadata) and retrieves the
most relevant chunks for a query.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ai.rag.chunking import chunk_text
from app.ai.rag.embeddings import Embedder, HashingEmbedder
from app.ai.rag.reranker import rerank
from app.ai.rag.vector_store import (
    InMemoryVectorStore,
    SearchHit,
    VectorRecord,
    get_vector_store,
)
from app.core.config import Settings, get_settings


@dataclass
class RetrievedChunk:
    """A retrieved chunk surfaced to services/endpoints."""

    text: str
    score: float
    note_id: int | None
    note_title: str | None


class Retriever:
    """RAG retriever over user-scoped note chunks."""

    def __init__(
        self,
        *,
        store: InMemoryVectorStore | None = None,
        embedder: Embedder | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._store = store or get_vector_store()
        self._embedder = embedder or HashingEmbedder(self._settings.embedding_dim)

    # ── Indexing ───────────────────────────────────────────────────────────
    def index_note(
        self, *, user_id: int, note_id: int, title: str, content: str
    ) -> int:
        """(Re)index a single note. Returns number of chunks indexed."""
        # Remove any stale chunks for this note first.
        self._store.delete_where({"note_id": note_id})
        document = f"{title}\n\n{content}".strip()
        chunks = chunk_text(
            document,
            chunk_size=self._settings.rag_chunk_size,
            overlap=self._settings.rag_chunk_overlap,
        )
        for i, chunk in enumerate(chunks):
            self._store.add(
                VectorRecord(
                    id=f"u{user_id}-n{note_id}-c{i}",
                    text=chunk,
                    embedding=self._embedder.embed(chunk),
                    metadata={
                        "user_id": user_id,
                        "note_id": note_id,
                        "note_title": title,
                    },
                )
            )
        return len(chunks)

    def remove_note(self, note_id: int) -> int:
        """Drop all chunks for a note. Returns number removed."""
        return self._store.delete_where({"note_id": note_id})

    # ── Retrieval ──────────────────────────────────────────────────────────
    def retrieve(
        self, *, user_id: int, query: str, top_k: int | None = None
    ) -> list[RetrievedChunk]:
        """Retrieve the most relevant chunks for a user's query."""
        k = top_k or self._settings.rag_top_k
        q_emb = self._embedder.embed(query)
        hits: list[SearchHit] = self._store.search(
            q_emb, top_k=max(k * 3, k), where={"user_id": user_id}
        )
        hits = rerank(query, hits, top_k=k)
        return [
            RetrievedChunk(
                text=h.record.text,
                score=h.score,
                note_id=h.record.metadata.get("note_id"),
                note_title=h.record.metadata.get("note_title"),
            )
            for h in hits
        ]
