"""Application configuration via pydantic-settings.

All runtime configuration is read from environment variables / a local ``.env``
file. The app is offline-first: with NO keys set it falls back to the
deterministic ``EchoProvider`` and an in-memory vector store, so every endpoint
and every test runs green without external services.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- App ---
    app_name: str = "Deep Dive — PDF to EPUB GenAI"
    app_version: str = "2.0.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # --- API / security ---
    api_v1_prefix: str = "/api/v1"
    # Optional simple API key. When empty, auth is a no-op (offline-first).
    api_key: str = ""

    # --- LLM provider selection ---
    # "auto" picks Gemini when a Google key is present, else EchoProvider.
    llm_provider: str = "auto"
    llm_model: str = "gemini-3.1-flash-lite"
    llm_temperature: float = 0.2

    # Google Gemini. Accept either env var name commonly used in the wild.
    google_api_key: str = Field(default="", validation_alias="GOOGLE_API_KEY")
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")

    # --- Document parsing (LlamaParse / llama-cloud) ---
    llama_cloud_api_key: str = Field(default="", validation_alias="LLAMA_CLOUD_API_KEY")
    llama_parse_tier: str = "agentic"

    # --- RAG ---
    embedding_dim: int = 256
    rag_top_k: int = 4
    chunk_size: int = 800
    chunk_overlap: int = 120

    # --- Storage ---
    # Generated EPUBs and other artifacts (gitignored).
    output_dir: str = "generated"

    @property
    def resolved_google_key(self) -> str:
        """Return whichever Google/Gemini key is configured (Gemini takes precedence)."""
        return self.gemini_api_key or self.google_api_key

    @property
    def has_llm_key(self) -> bool:
        return bool(self.resolved_google_key)

    @property
    def has_llama_key(self) -> bool:
        return bool(self.llama_cloud_api_key)


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (used as a FastAPI dependency)."""
    return Settings()
