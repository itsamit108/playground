"""Retriever — orchestrates embed -> vector search -> rerank.

Owns a single in-memory vector store instance and the embedder. Construct one
per process (the service layer holds it as a singleton).
"""

from __future__ import annotations

from app.ai.rag.chunking import chunk_text
from app.ai.rag.embeddings import Embedder, HashingEmbedder
from app.ai.rag.reranker import rerank
from app.ai.rag.vector_store import InMemoryVectorStore, SearchHit, StoredItem


class Retriever:
    def __init__(
        self,
        embedder: Embedder | None = None,
        store: InMemoryVectorStore | None = None,
        *,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):
        self.embedder = embedder or HashingEmbedder()
        self.store = store or InMemoryVectorStore()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def ingest(self, text: str, *, source: str = "inline", metadata: dict[str, str] | None = None) -> int:
        """Chunk + embed + store. Returns number of chunks added."""
        chunks = chunk_text(
            text, source=source, chunk_size=self.chunk_size, overlap=self.chunk_overlap
        )
        items = [
            StoredItem(
                text=c.text,
                source=c.source,
                embedding=self.embedder.embed(c.text),
                metadata={**(metadata or {}), "chunk": str(c.index)},
            )
            for c in chunks
        ]
        self.store.add_many(items)
        return len(items)

    def retrieve(self, query: str, *, top_k: int = 4) -> list[SearchHit]:
        q_emb = self.embedder.embed(query)
        # Over-fetch then rerank for better precision.
        hits = self.store.search(q_emb, top_k=max(top_k * 3, top_k))
        return rerank(query, hits, top_k=top_k)

    def count(self) -> int:
        return self.store.count()
