"""RAG retrieval request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Document text to index.")
    source: str = Field(default="inline", description="Source label / metadata.")


class IngestResponse(BaseModel):
    chunks_indexed: int
    total_chunks: int


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(default=3, ge=1, le=20)


class RetrievedChunk(BaseModel):
    text: str
    score: float


class QueryResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]
