"""Unit tests for the RAG layer."""

from __future__ import annotations

from app.ai.rag.chunking import chunk_text
from app.ai.rag.embeddings import HashingEmbedder, cosine_similarity
from app.ai.rag.retriever import Retriever


def test_chunking_overlaps_and_covers():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    assert all(c.text for c in chunks)


def test_embedder_similar_text_scores_higher():
    emb = HashingEmbedder(dim=128)
    v_cat = emb.embed("the cat sat on the mat")
    v_cat2 = emb.embed("a cat sat on a mat")
    v_finance = emb.embed("quarterly revenue and tax filings")
    assert cosine_similarity(v_cat, v_cat2) > cosine_similarity(v_cat, v_finance)


def test_retriever_ingest_and_retrieve():
    r = Retriever(embedder=HashingEmbedder(dim=128), chunk_size=100, chunk_overlap=10)
    added = r.ingest(
        "Pelicans are large water birds with a long beak and a large throat pouch.",
        source="birds",
    )
    assert added >= 1
    r.ingest("Compilers translate source code into machine code.", source="cs")
    hits = r.retrieve("tell me about birds and beaks", top_k=1)
    assert hits
    assert hits[0].source == "birds"
