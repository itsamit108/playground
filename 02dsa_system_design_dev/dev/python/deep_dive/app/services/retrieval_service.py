"""Retrieval service — wraps the RAG retriever as a process-singleton.

This is the only place the API layer touches RAG; routers never import the vector
store directly.
"""

from __future__ import annotations

from app.ai.rag.retriever import Retriever
from app.core.config import Settings
from app.schemas.retrieval import (
    IngestResponse,
    RetrievalResponse,
    RetrievedChunk,
)

_retriever: Retriever | None = None


def get_retriever(settings: Settings) -> Retriever:
    global _retriever
    if _retriever is None:
        from app.ai.rag.embeddings import HashingEmbedder

        _retriever = Retriever(
            embedder=HashingEmbedder(dim=settings.embedding_dim),
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
    return _retriever


class RetrievalService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.retriever = get_retriever(settings)

    def ingest(self, text: str, *, source: str, metadata: dict[str, str]) -> IngestResponse:
        added = self.retriever.ingest(text, source=source, metadata=metadata)
        return IngestResponse(
            source=source, chunks_added=added, total_chunks=self.retriever.count()
        )

    def retrieve(self, query: str, *, top_k: int) -> RetrievalResponse:
        hits = self.retriever.retrieve(query, top_k=top_k)
        return RetrievalResponse(
            query=query,
            results=[
                RetrievedChunk(text=h.text, source=h.source, score=round(h.score, 4)) for h in hits
            ],
        )
