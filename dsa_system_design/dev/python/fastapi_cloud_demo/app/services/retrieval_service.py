"""Retrieval (RAG) service.

Wraps the ai/rag retriever as an application use case. Owns a process-wide
retriever instance seeded with facts about this service.
"""

from __future__ import annotations

from app.ai.rag.retriever import Retriever


class RetrievalService:
    """Application service for document ingest + retrieval."""

    def __init__(self, retriever: Retriever | None = None) -> None:
        self._retriever = retriever or Retriever()

    def ingest(self, doc_id: str, text: str) -> int:
        return self._retriever.add_document(doc_id, text)

    def retrieve(self, query: str, *, top_k: int = 3) -> list[dict]:
        results = self._retriever.retrieve(query, top_k=top_k)
        return [
            {
                "id": item.document.id,
                "text": item.document.text,
                "score": round(item.score, 6),
                "metadata": item.document.metadata,
            }
            for item in results
        ]


retrieval_service = RetrievalService()
