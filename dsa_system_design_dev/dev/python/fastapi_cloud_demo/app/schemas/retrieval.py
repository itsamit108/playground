"""Retrieval (RAG) request/response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RetrievalQuery(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class RetrievedChunk(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict[str, Any]


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]


class IngestRequest(BaseModel):
    doc_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)


class IngestResponse(BaseModel):
    doc_id: str
    chunks_added: int
