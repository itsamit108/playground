"""Unit tests for the RAG building blocks (offline, no DB)."""

from __future__ import annotations

from app.ai.rag.chunking import chunk_text
from app.ai.rag.embeddings import HashingEmbedder, cosine_similarity
from app.ai.rag.retriever import Retriever
from app.ai.rag.vector_store import InMemoryVectorStore


def test_chunking_overlap_and_word_boundaries():
    text = "word " * 300  # 1500 chars
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)
    # No chunk should start/end mid-word (only whole "word" tokens).
    for c in chunks:
        assert set(c.split()) == {"word"}


def test_embedding_is_deterministic_and_normalised():
    emb = HashingEmbedder(dim=64)
    v1 = emb.embed("the quick brown fox")
    v2 = emb.embed("the quick brown fox")
    assert v1 == v2
    assert abs(sum(x * x for x in v1) - 1.0) < 1e-6


def test_similar_text_scores_higher():
    emb = HashingEmbedder(dim=128)
    q = emb.embed("apollo launch schedule")
    near = emb.embed("the apollo launch is scheduled for Q3")
    far = emb.embed("buy milk and eggs from the store")
    assert cosine_similarity(q, near) > cosine_similarity(q, far)


def test_retriever_scopes_by_user():
    store = InMemoryVectorStore()
    r = Retriever(store=store)
    r.index_note(user_id=1, note_id=1, title="Apollo", content="Launch in Q3")
    r.index_note(user_id=2, note_id=2, title="Other", content="Launch in Q3 too")
    hits = r.retrieve(user_id=1, query="when is the launch", top_k=5)
    assert hits
    assert all(h.note_id == 1 for h in hits)
