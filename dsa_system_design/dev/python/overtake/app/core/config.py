"""Application configuration via pydantic-settings.

Reads from environment / .env. Provides a cached `Settings` singleton through
`get_settings()`. Everything has a safe offline default so the app and the test
suite run with zero external services and zero API keys.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object. Field names map to env vars (case-insensitive)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────
    app_name: str = "Overtake"
    app_version: str = "0.2.0"
    app_description: str = (
        "Multi-user multimedia note-taking API with a built-in RAG/agent "
        "assistant over your own notes."
    )
    log_level: str = "INFO"

    # ── Database ──────────────────────────────────────────────────────────
    # Default targets LocalStack RDS PostgreSQL. Tests override with SQLite.
    database_url: str = "postgresql://overtake:overtake123@localhost:4510/overtake_db"

    # ── AWS / S3 (LocalStack) ─────────────────────────────────────────────
    aws_endpoint_url: str = "http://localhost:4566"
    aws_region: str = "us-east-1"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    s3_bucket_name: str = "overtake-media"

    # ── JWT auth ──────────────────────────────────────────────────────────
    jwt_secret_key: str = "super-secret-change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # ── AI / LLM provider ─────────────────────────────────────────────────
    # Provider selection. "echo" is the offline, deterministic default that
    # needs no network and no keys. "openai"/"anthropic" are extension points.
    llm_provider: str = "echo"
    llm_model: str = "echo-1"
    llm_api_key: str | None = None
    llm_temperature: float = 0.2

    # ── RAG ───────────────────────────────────────────────────────────────
    embedding_dim: int = 256
    rag_chunk_size: int = 400
    rag_chunk_overlap: int = 40
    rag_top_k: int = 4


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
