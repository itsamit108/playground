"""Application configuration via pydantic-settings.

Reads from environment variables and an optional ``.env`` file. Everything has a
safe default so the app boots out of the box with zero configuration and zero
external services or API keys.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "FastAPI Cloud Demo"
    app_version: str = "0.2.0"
    environment: str = "local"
    debug: bool = False

    # --- API ---
    api_v1_prefix: str = "/api/v1"

    # --- Auth (optional, no-op by default) ---
    # When unset, the api-key dependency is a no-op so the demo runs open.
    api_key: str | None = None

    # --- Counter feature ---
    counter_interval_seconds: float = 1.0
    counter_start: int = 0

    # --- LLM provider selection ---
    # Default provider is the offline EchoProvider so the app needs no keys.
    # Supported: "echo", "ollama", "openai".
    llm_provider: str = "echo"
    llm_model: str = "echo-1"
    llm_temperature: float = 0.2

    # OpenAI-compatible provider (optional)
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"

    # Ollama provider (optional, local, no cloud key)
    ollama_base_url: str = "http://localhost:11434"

    # --- Observability ---
    log_level: str = "INFO"
    log_json: bool = False


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
