"""Observability + host metrics.

Holds the system-specs collection logic (psutil + best-effort GPU via
nvidia-smi), folded here from the original ``app/main.py``. This is the natural
home for host/process telemetry. In production this layer is where Langfuse /
OpenTelemetry GenAI tracing would be wired (recommended extension point).
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from typing import Any

import psutil


def _gb(value: float) -> float:
    return round(value / (1024**3), 2)


def gpu_specs() -> dict[str, Any]:
    """Best-effort GPU details via nvidia-smi. Never raises."""
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,driver_version",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=3,
        )
        return {
            "detected": True,
            "source": "nvidia-smi",
            "gpus": [
                dict(
                    zip(
                        ["name", "memory_total_mb", "memory_used_mb", "driver_version"],
                        [value.strip() for value in line.split(",")],
                    )
                )
                for line in output.splitlines()
            ],
        }
    except Exception:
        return {"detected": False, "message": "No GPU detected or GPU tools unavailable"}


def system_specs() -> dict[str, Any]:
    """Collect OS / Python / CPU / memory / disk / GPU / process specs."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "cpu": {
            "logical_cores": os.cpu_count(),
            "physical_cores": psutil.cpu_count(logical=False),
            "usage_percent": psutil.cpu_percent(interval=0.1),
        },
        "memory": {
            "total_gb": _gb(memory.total),
            "available_gb": _gb(memory.available),
            "used_gb": _gb(memory.used),
            "usage_percent": memory.percent,
        },
        "disk": {
            "total_gb": _gb(disk.total),
            "free_gb": _gb(disk.free),
            "used_gb": _gb(disk.used),
            "usage_percent": disk.percent,
        },
        "gpu": gpu_specs(),
        "process": {"pid": os.getpid()},
    }
