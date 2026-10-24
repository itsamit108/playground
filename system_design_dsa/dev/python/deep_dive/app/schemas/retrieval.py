"""Retrieval / RAG schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Ingest raw text into the vector store."""

    text: str = Field(..., min_length=1)
    source: str = "inline"
    metadata: dict[str, str] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    source: str
    chunks_added: int
    total_chunks: int


class RetrievedChunk(BaseModel):
    text: str
    source: str
    score: float


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=4, ge=1, le=50)


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]
