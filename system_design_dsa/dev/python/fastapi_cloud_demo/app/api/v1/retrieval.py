"""RAG endpoints -> retrieval_service. No vector-store access here."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_retrieval_service
from app.schemas.retrieval import (
    IngestRequest,
    IngestResponse,
    RetrievalQuery,
    RetrievalResponse,
    RetrievedChunk,
)
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/query", response_model=RetrievalResponse)
def query(
    request: RetrievalQuery,
    service: RetrievalService = Depends(get_retrieval_service),
) -> RetrievalResponse:
    results = service.retrieve(request.query, top_k=request.top_k)
    return RetrievalResponse(
        query=request.query,
        results=[RetrievedChunk(**item) for item in results],
    )


@router.post("/ingest", response_model=IngestResponse)
def ingest(
    request: IngestRequest,
    service: RetrievalService = Depends(get_retrieval_service),
) -> IngestResponse:
    added = service.ingest(request.doc_id, request.text)
    return IngestResponse(doc_id=request.doc_id, chunks_added=added)
