"""Ingest a text file (or stdin) into the RAG vector store and run a sample query.

Usage:
    uv run python scripts/ingest.py path/to/file.txt "your query"
"""

from __future__ import annotations

import sys
from pathlib import Path

from app.core.config import get_settings
from app.services.retrieval_service import RetrievalService


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: ingest.py <file.txt> [query]", file=sys.stderr)
        return 2

    path = Path(argv[1])
    text = path.read_text(encoding="utf-8") if path.exists() else argv[1]
    query = argv[2] if len(argv) > 2 else "summary"

    service = RetrievalService(get_settings())
    res = service.ingest(text, source=path.name if path.exists() else "inline", metadata={})
    print(f"Ingested {res.chunks_added} chunk(s); total={res.total_chunks}")

    out = service.retrieve(query, top_k=3)
    print(f"\nTop matches for {query!r}:")
    for hit in out.results:
        print(f"  [{hit.score:.3f}] ({hit.source}) {hit.text[:100]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
