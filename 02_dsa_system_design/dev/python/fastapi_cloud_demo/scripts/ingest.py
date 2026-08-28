"""Ingest a text file (or inline text) into the RAG store and run a sample query.

Usage:
    uv run python scripts/ingest.py path/to/file.txt "your query"
    uv run python scripts/ingest.py "some inline text" "query"
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `app` importable when run directly; the project is not installed.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.retrieval_service import RetrievalService  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: ingest.py <file.txt|text> [query]", file=sys.stderr)
        return 2

    path = Path(argv[1])
    text = path.read_text(encoding="utf-8") if path.exists() else argv[1]
    doc_id = path.name if path.exists() else "inline"
    query = argv[2] if len(argv) > 2 else "summary"

    service = RetrievalService()
    added = service.ingest(doc_id, text)
    print(f"Ingested document {doc_id!r}: {added} chunk(s)")

    print(f"\nTop matches for {query!r}:")
    for hit in service.retrieve(query, top_k=3):
        print(f"  [{hit['score']:.3f}] ({hit['id']}) {hit['text'][:100]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
