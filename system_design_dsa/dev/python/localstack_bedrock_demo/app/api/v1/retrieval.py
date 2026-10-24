"""RAG endpoints -> retrieval_service."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, RetrievalServiceDep
from app.schemas.retrieval import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
)

router = APIRouter(prefix="/retrieval", tags=["retrieval"], dependencies=[AuthDep])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest, service: RetrievalServiceDep) -> IngestResponse:
    """Chunk, embed, and index a document for retrieval."""
    return service.ingest(req)


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest, service: RetrievalServiceDep) -> QueryResponse:
    """Retrieve the most relevant chunks for a query."""
    return service.query(req)
