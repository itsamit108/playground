"""RAG endpoints -> retrieval_service."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import RetrievalServiceDep, require_auth
from app.schemas.retrieval import (
    IngestRequest,
    IngestResponse,
    RetrievalRequest,
    RetrievalResponse,
)

router = APIRouter(prefix="/retrieval", tags=["retrieval"], dependencies=[Depends(require_auth)])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest, service: RetrievalServiceDep) -> IngestResponse:
    return service.ingest(req.text, source=req.source, metadata=req.metadata)


@router.post("/search", response_model=RetrievalResponse)
async def search(req: RetrievalRequest, service: RetrievalServiceDep) -> RetrievalResponse:
    return service.retrieve(req.query, top_k=req.top_k)
