"""Document chunking.

Splits text into overlapping, word-bounded chunks suitable for embedding.
"""

from __future__ import annotations


def chunk_text(
    text: str, *, chunk_size: int = 400, overlap: int = 40
) -> list[str]:
    """Split text into overlapping chunks of roughly `chunk_size` characters.

    Chunks break on whitespace so words are not split. `overlap` characters of
    trailing context are repeated at the start of the next chunk to preserve
    continuity across boundaries.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            # Back up to the last space to avoid splitting a word.
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks
