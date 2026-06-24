"""Structured logging setup.

A tiny, dependency-free structured logger: emits single-line key=value records
so logs stay greppable locally and parseable in production aggregators.
"""

from __future__ import annotations

import logging
import sys


class _KeyValueFormatter(logging.Formatter):
    """Format records as `ts level logger msg [extra=...]`."""

    def format(self, record: logging.LogRecord) -> str:
        base = (
            f"ts={self.formatTime(record, '%Y-%m-%dT%H:%M:%S')} "
            f"level={record.levelname} "
            f"logger={record.name} "
            f"msg={record.getMessage()!r}"
        )
        extra = getattr(record, "extra_fields", None)
        if extra:
            kv = " ".join(f"{k}={v!r}" for k, v in extra.items())
            base = f"{base} {kv}"
        return base


_CONFIGURED = False


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger once with a key=value formatter."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_KeyValueFormatter())
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
