"""Document chunking utilities."""

from __future__ import annotations


def chunk_text(text: str, *, chunk_size: int = 400, overlap: int = 40) -> list[str]:
    """Split text into overlapping character chunks.

    Simple and dependency-free. Production systems would use token-aware
    splitters (LlamaIndex / LangChain / Haystack).
    """
    text = text.strip()
    if not text:
        return []
    if chunk_size <= 0:
        return [text]

    chunks: list[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += step
    return chunks
