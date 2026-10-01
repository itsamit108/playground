"""Object/blob storage adapter.

Local-filesystem default. Swap for S3 / GCS / Azure Blob behind this interface.
"""

from __future__ import annotations

from pathlib import Path


class LocalStorage:
    """Stores blobs under a local directory."""

    def __init__(self, root: str = "./.storage") -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def write(self, name: str, data: bytes) -> str:
        path = self._root / name
        path.write_bytes(data)
        return str(path)

    def read(self, name: str) -> bytes:
        return (self._root / name).read_bytes()
