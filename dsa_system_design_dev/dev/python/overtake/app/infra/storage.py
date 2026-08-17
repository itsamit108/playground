"""Object storage adapter (S3 via LocalStack).

Wraps boto3 so services never import boto3 directly. The bucket is ensured on
first use. All methods raise nothing fatal for best-effort delete paths.
"""

from __future__ import annotations

from typing import Protocol

import boto3
from botocore.exceptions import ClientError

from app.core.config import Settings, get_settings


class ObjectStorage(Protocol):
    """Minimal object-storage contract used by services."""

    def ensure_bucket(self) -> None: ...
    def put(self, key: str, body: bytes, content_type: str) -> None: ...
    def get(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...


class S3Storage:
    """boto3-backed S3 storage targeting a configurable endpoint."""

    def __init__(self, settings: Settings) -> None:
        self._bucket = settings.s3_bucket_name
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.aws_endpoint_url,
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def put(self, key: str, body: bytes, content_type: str) -> None:
        self._client.put_object(
            Bucket=self._bucket, Key=key, Body=body, ContentType=content_type
        )

    def get(self, key: str) -> bytes:
        obj = self._client.get_object(Bucket=self._bucket, Key=key)
        return obj["Body"].read()

    def delete(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except ClientError:
            pass  # best-effort cleanup


def get_storage(settings: Settings | None = None) -> S3Storage:
    """Construct the S3 storage adapter from settings."""
    return S3Storage(settings or get_settings())
