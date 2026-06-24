"""Retriever: ties chunking + vector store + reranking together.

Owns a default in-memory document store seeded with facts about this service so
the retrieval endpoint returns something sensible out of the box.
"""

from __future__ import annotations

from app.ai.rag.chunking import chunk_text
from app.ai.rag.reranker import rerank
from app.ai.rag.vector_store import InMemoryVectorStore, ScoredDocument

# Seed corpus describing this very service.
_SEED_DOCS: list[tuple[str, str]] = [
    (
        "counter",
        "The FastAPI Cloud Demo runs a background counter task started in the "
        "app lifespan. It increments an in-memory counter once per second. The "
        "counter resets when the instance restarts or scales to zero.",
    ),
    (
        "specs",
        "The system specs feature reports OS, Python version, CPU cores and "
        "usage, memory, disk, and best-effort GPU details via psutil and "
        "nvidia-smi. It is exposed at /specs and via a system router.",
    ),
    (
        "chat",
        "The chat feature is model-agnostic. The default provider is an offline "
        "EchoProvider that needs no API keys. Ollama and OpenAI-compatible "
        "providers are also available via configuration.",
    ),
    (
        "agents",
        "The ops-assistant agent answers questions about the host system by "
        "calling the get_system_specs and summarize_specs tools, then phrasing "
        "the answer with the configured LLM.",
    ),
]


class Retriever:
    """Default retriever over an in-memory seeded corpus."""

    def __init__(self) -> None:
        self.store = InMemoryVectorStore()
        self._seed()

    def _seed(self) -> None:
        for doc_id, text in _SEED_DOCS:
            for index, chunk in enumerate(chunk_text(text, chunk_size=400, overlap=40)):
                self.store.add(f"{doc_id}-{index}", chunk, metadata={"source": doc_id})

    def add_document(self, doc_id: str, text: str) -> int:
        chunks = chunk_text(text, chunk_size=400, overlap=40)
        for index, chunk in enumerate(chunks):
            self.store.add(f"{doc_id}-{index}", chunk, metadata={"source": doc_id})
        return len(chunks)

    def retrieve(self, query: str, *, top_k: int = 3) -> list[ScoredDocument]:
        candidates = self.store.search(query, top_k=max(top_k, 5))
        return rerank(query, candidates)[:top_k]
