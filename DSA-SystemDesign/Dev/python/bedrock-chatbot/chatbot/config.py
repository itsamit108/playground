"""Centralised configuration loaded from environment / .env file."""

import os
from dotenv import load_dotenv

load_dotenv()

AWS_ENDPOINT_URL: str = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "test")

BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-8b-instruct-v1:0")
SYSTEM_PROMPT: str = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful, concise AI assistant. Answer questions clearly and briefly.",
)
