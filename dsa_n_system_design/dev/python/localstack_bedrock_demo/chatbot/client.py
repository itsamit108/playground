"""Thin wrapper around the Bedrock Runtime client."""

from __future__ import annotations

import boto3
from botocore.config import Config

from chatbot.config import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
)


def get_bedrock_runtime_client():
    """Return a boto3 bedrock-runtime client pointed at LocalStack."""
    return boto3.client(
        "bedrock-runtime",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(
            retries={"max_attempts": 5, "mode": "adaptive"},
            read_timeout=600,  # first call may pull the Ollama model
            connect_timeout=30,
        ),
    )


def get_bedrock_client():
    """Return a boto3 bedrock (control-plane) client pointed at LocalStack."""
    return boto3.client(
        "bedrock",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
