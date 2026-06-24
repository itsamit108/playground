"""RAG use case: ingest documents + answer retrieval queries.

Uses a process-wide Retriever so ingested docs persist across requests within
the running service.
"""

from __future__ import annotations

from app.ai.rag.retriever import Retriever
from app.schemas.retrieval import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
)

_retriever = Retriever()


def get_retriever() -> Retriever:
    return _retriever


class RetrievalService:
    def __init__(self, retriever: Retriever | None = None) -> None:
        self.retriever = retriever or get_retriever()

    def ingest(self, req: IngestRequest) -> IngestResponse:
        added = self.retriever.index(req.text, metadata={"source": req.source})
        return IngestResponse(
            chunks_indexed=added, total_chunks=len(self.retriever.store)
        )

    def query(self, req: QueryRequest) -> QueryResponse:
        hits = self.retriever.retrieve(req.query, k=req.k)
        return QueryResponse(
            query=req.query,
            results=[RetrievedChunk(text=t, score=s) for t, s in hits],
        )
