"""Unit tests for the Conversation class (mocked Bedrock calls)."""

from unittest.mock import MagicMock, patch

import pytest

from chatbot.conversation import Conversation


@pytest.fixture
def mock_bedrock_response():
    """A minimal Converse API response."""
    return {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": "Hello! How can I help you?"}],
            }
        },
        "stopReason": "end_turn",
        "usage": {"inputTokens": 10, "outputTokens": 8, "totalTokens": 18},
    }


@patch("chatbot.conversation.get_bedrock_runtime_client")
def test_send_returns_assistant_text(mock_client_factory, mock_bedrock_response):
    """send() should return the assistant's text from the Converse response."""
    mock_client = MagicMock()
    mock_client.converse.return_value = mock_bedrock_response
    mock_client_factory.return_value = mock_client

    convo = Conversation(model_id="test-model", system_prompt="Be helpful.")
    reply = convo.send("Hi there!")

    assert reply == "Hello! How can I help you?"
    assert convo.turn_count == 1
    assert len(convo.messages) == 2  # user + assistant


@patch("chatbot.conversation.get_bedrock_runtime_client")
def test_reset_clears_history(mock_client_factory, mock_bedrock_response):
    """reset() should empty the message list."""
    mock_client = MagicMock()
    mock_client.converse.return_value = mock_bedrock_response
    mock_client_factory.return_value = mock_client

    convo = Conversation(model_id="test-model", system_prompt="Be helpful.")
    convo.send("Hello")
    convo.reset()

    assert convo.turn_count == 0
    assert len(convo.messages) == 0


@patch("chatbot.conversation.get_bedrock_runtime_client")
def test_multi_turn_conversation(mock_client_factory):
    """Multiple send() calls should accumulate history."""
    responses = [
        {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{"text": f"Reply {i}"}],
                }
            }
        }
        for i in range(3)
    ]

    mock_client = MagicMock()
    mock_client.converse.side_effect = responses
    mock_client_factory.return_value = mock_client

    convo = Conversation(model_id="test-model", system_prompt="Be helpful.")

    for i in range(3):
        reply = convo.send(f"Message {i}")
        assert reply == f"Reply {i}"

    assert convo.turn_count == 3
    assert len(convo.messages) == 6  # 3 user + 3 assistant


def test_extract_text_handles_missing_content():
    """_extract_text should return a fallback for malformed responses."""
    assert Conversation._extract_text({}) == "[no response]"
    assert Conversation._extract_text({"output": {}}) == "[no response]"
