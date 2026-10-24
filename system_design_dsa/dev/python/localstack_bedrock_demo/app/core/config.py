"""Application configuration via pydantic-settings (reads .env).

Replaces the old ``chatbot/config.py`` module-level constants with a typed
``Settings`` object plus a cached ``get_settings()`` accessor used everywhere
through FastAPI dependency injection.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────
    app_name: str = "LocalStack Bedrock GenAI Service"
    environment: str = "local"
    log_level: str = "INFO"

    # ── Auth (optional API key; no-op when unset) ────────────────
    api_key: str | None = None

    # ── AWS / LocalStack Bedrock ─────────────────────────────────
    aws_endpoint_url: str = "http://localhost:4566"
    aws_region: str = "us-east-1"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"

    # ── LLM provider selection ───────────────────────────────────
    # "auto" -> use Bedrock when reachable, otherwise fall back to echo.
    # "bedrock" -> force Bedrock. "echo" -> force the offline EchoProvider.
    llm_provider: str = "auto"

    bedrock_model_id: str = "ollama.llama3.2"
    system_prompt: str = (
        "You are a helpful, concise AI assistant. "
        "Answer questions clearly and briefly."
    )

    # Seconds boto3 waits before deciding LocalStack/Bedrock is unreachable.
    bedrock_connect_timeout: int = 5


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
