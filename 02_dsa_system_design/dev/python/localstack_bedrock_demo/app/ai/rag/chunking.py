"""Text chunking for RAG ingestion."""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 240, overlap: int = 40) -> list[str]:
    """Split text into overlapping word-based chunks.

    Simple, dependency-free chunker. Replace with LlamaIndex / Haystack
    splitters for production.
    """
    words = text.split()
    if not words:
        return []
    if chunk_size <= 0:
        return [" ".join(words)]

    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        chunk = words[start : start + chunk_size]
        if chunk:
            chunks.append(" ".join(chunk))
        if start + chunk_size >= len(words):
            break
    return chunks
