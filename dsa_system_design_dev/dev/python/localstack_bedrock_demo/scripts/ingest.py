"""Ingest sample documents into the RAG retriever (runnable).

Usage:
    uv run python -m scripts.ingest [path-to-text-file ...]

With no args it ingests a tiny built-in sample so the retrieval endpoints have
something to return.
"""

from __future__ import annotations

import sys
from pathlib import Path

from app.schemas.retrieval import IngestRequest, QueryRequest
from app.services.retrieval_service import RetrievalService

SAMPLE = (
    "LocalStack emulates AWS services locally. Bedrock support lets you call "
    "the Converse API against Ollama models with no AWS account. This service "
    "wraps Bedrock behind a model-agnostic LLMClient with an offline echo "
    "fallback, a tool-using agent, and a small RAG retrieval pipeline."
)


def main() -> None:
    service = RetrievalService()
    paths = sys.argv[1:]
    if paths:
        for p in paths:
            text = Path(p).read_text(encoding="utf-8")
            res = service.ingest(IngestRequest(text=text, source=p))
            print(f"Ingested {res.chunks_indexed} chunks from {p}")
    else:
        res = service.ingest(IngestRequest(text=SAMPLE, source="sample"))
        print(f"Ingested {res.chunks_indexed} chunks from built-in sample")

    demo = service.query(QueryRequest(query="What is LocalStack Bedrock?", k=2))
    print("\nDemo query: 'What is LocalStack Bedrock?'")
    for r in demo.results:
        print(f"  [{r.score:.3f}] {r.text[:80]}...")


if __name__ == "__main__":
    main()
