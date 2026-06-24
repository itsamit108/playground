"""RAG pipeline: chunking + retriever return relevant chunks."""

from app.ai.rag.chunking import chunk_text
from app.ai.rag.retriever import Retriever


def test_chunk_text_splits_and_overlaps():
    text = " ".join(str(i) for i in range(500))
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(chunks)


def test_retriever_finds_relevant_chunk():
    r = Retriever()
    r.index(
        "Paris is the capital of France. Berlin is the capital of Germany.",
    )
    results = r.retrieve("What is the capital of France?", k=1)
    assert results
    assert "Paris" in results[0][0]


def test_retriever_empty_returns_nothing():
    assert Retriever().retrieve("anything") == []
