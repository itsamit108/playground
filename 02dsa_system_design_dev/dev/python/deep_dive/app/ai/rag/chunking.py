"""Text chunking for RAG ingestion."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str
    index: int


def chunk_text(
    text: str,
    *,
    source: str = "inline",
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[Chunk]:
    """Split text into overlapping character windows on whitespace boundaries.

    Simple, dependency-free chunker. In production this is where you would slot
    LlamaIndex / Haystack node parsers.
    """
    text = text.strip()
    if not text:
        return []
    if chunk_size <= 0:
        return [Chunk(text=text, source=source, index=0)]
    overlap = max(0, min(overlap, chunk_size - 1))

    chunks: list[Chunk] = []
    start = 0
    idx = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        # Try to break on the last whitespace within the window for clean cuts.
        if end < n:
            ws = text.rfind(" ", start, end)
            if ws > start:
                end = ws
        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(text=piece, source=source, index=idx))
            idx += 1
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks
