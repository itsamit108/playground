"""System service.

Exposes host system specs (the psutil/GPU logic from the original main.py, now
living in ``infra/observability``) as an application use case.
"""

from __future__ import annotations

from typing import Any

from app.infra.observability import system_specs


class SystemService:
    """Application service for host system information."""

    def specs(self) -> dict[str, Any]:
        return system_specs()


system_service = SystemService()
