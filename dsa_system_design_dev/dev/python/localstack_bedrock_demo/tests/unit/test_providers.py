"""Unit tests for LLM providers (EchoProvider + BedrockProvider, mocked boto3).

Migrated from the original tests/test_conversation.py — the Converse-API
response parsing + multi-turn behaviour now lives in BedrockProvider, exercised
here with a mocked boto3 client (no live LocalStack).
"""

from unittest.mock import MagicMock

import pytest

from app.ai.models.providers import BedrockProvider, EchoProvider
from app.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(llm_provider="echo")


async def test_echo_provider_echoes_last_user_message(settings):
    provider = EchoProvider()
    result = await provider.generate(
        messages=[{"role": "user", "content": "Hi there!"}]
    )
    assert result["text"] == "Echo: Hi there!"
    assert result["model"] == "echo-1"


async def test_echo_provider_handles_empty(settings):
    provider = EchoProvider()
    result = await provider.generate(messages=[])
    assert result["text"] == "Echo: (no input)"


async def test_bedrock_provider_parses_converse_response(settings):
    provider = BedrockProvider(settings)
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": "Hello! How can I help you?"}],
            }
        },
        "usage": {"inputTokens": 10, "outputTokens": 8},
    }
    provider._runtime = mock_client  # inject mock

    result = await provider.generate(
        messages=[
            {"role": "system", "content": "Be helpful."},
            {"role": "user", "content": "Hi"},
        ]
    )
    assert result["text"] == "Hello! How can I help you?"
    assert result["usage"]["input_tokens"] == 10
    # System message excluded from Bedrock messages; passed via `system` arg.
    _, kwargs = mock_client.converse.call_args
    assert kwargs["system"] == [{"text": "Be helpful."}]
    assert all(m["role"] != "system" for m in kwargs["messages"])


def test_bedrock_extract_text_handles_missing_content():
    from app.ai.models.providers import _extract_text

    assert _extract_text({}) == "[no response]"
    assert _extract_text({"output": {}}) == "[no response]"
