"""Retriever wiring chunking -> embeddings -> vector store -> rerank.

A small, fully-offline RAG pipeline so ``retrieval.py`` is a real feature.
"""

from __future__ import annotations

from app.ai.rag.chunking import chunk_text
from app.ai.rag.embeddings import HashingEmbedder
from app.ai.rag.reranker import rerank
from app.ai.rag.vector_store import Document, InMemoryVectorStore


class Retriever:
    """Index documents and retrieve the most relevant chunks for a query."""

    def __init__(self, embedder: HashingEmbedder | None = None) -> None:
        self.embedder = embedder or HashingEmbedder()
        self.store = InMemoryVectorStore()
        self._counter = 0

    def index(self, text: str, metadata: dict | None = None) -> int:
        """Chunk + embed + store a document. Returns number of chunks added."""
        chunks = chunk_text(text)
        for chunk in chunks:
            self.store.add(
                Document(
                    id=f"doc-{self._counter}",
                    text=chunk,
                    embedding=self.embedder.embed(chunk),
                    metadata=metadata or {},
                )
            )
            self._counter += 1
        return len(chunks)

    def retrieve(self, query: str, k: int = 3) -> list[tuple[str, float]]:
        """Return the top-k (chunk_text, score) results for a query."""
        if len(self.store) == 0:
            return []
        q_emb = self.embedder.embed(query)
        hits = self.store.search(q_emb, k=max(k * 2, k))
        candidates = [(doc.text, score) for doc, score in hits]
        return rerank(query, candidates, top_k=k)
