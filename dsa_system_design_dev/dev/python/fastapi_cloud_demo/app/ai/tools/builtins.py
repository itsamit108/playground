"""Built-in function tools, registered into the global ToolRegistry.

These are real, callable tools the ops-assistant agent can use. They read host
telemetry from the infra layer -- tools may use infra adapters, not services.
"""

from __future__ import annotations

from typing import Any

from app.ai.tools.registry import registry
from app.infra.observability import system_specs


@registry.tool(
    name="get_system_specs",
    description=(
        "Return the host system specs: OS, Python, CPU, memory, disk, GPU, and "
        "the current process id."
    ),
    parameters={"type": "object", "properties": {}},
)
def get_system_specs() -> dict[str, Any]:
    """Tool: return the current host system specs."""
    return system_specs()


@registry.tool(
    name="summarize_specs",
    description="Return a short one-line human summary of CPU/memory/disk usage.",
    parameters={"type": "object", "properties": {}},
)
def summarize_specs() -> str:
    """Tool: compact human-readable summary derived from system specs."""
    specs = system_specs()
    cpu = specs["cpu"]
    mem = specs["memory"]
    disk = specs["disk"]
    return (
        f"CPU {cpu['logical_cores']} cores @ {cpu['usage_percent']}% | "
        f"RAM {mem['used_gb']}/{mem['total_gb']} GB ({mem['usage_percent']}%) | "
        f"Disk {disk['used_gb']}/{disk['total_gb']} GB ({disk['usage_percent']}%)"
    )
