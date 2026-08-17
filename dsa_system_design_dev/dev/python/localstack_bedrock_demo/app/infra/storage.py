"""Object storage adapter (placeholder).

Seam for S3 (LocalStack provides S3). Defaults to a local temp-dir backed store.
"""

from __future__ import annotations

from pathlib import Path


class LocalStorage:
    def __init__(self, root: str | Path = ".storage") -> None:
        self.root = Path(root)

    def put(self, key: str, data: bytes) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / key
        path.write_bytes(data)
        return path

    def get(self, key: str) -> bytes | None:
        path = self.root / key
        return path.read_bytes() if path.exists() else None


def get_storage() -> LocalStorage:
    return LocalStorage()
