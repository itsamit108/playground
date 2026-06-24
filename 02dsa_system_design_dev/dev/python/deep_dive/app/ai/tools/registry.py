"""Tool registry — function tools with JSON schemas and permissions.

This is the internal tool registry. Per the architecture doc, MCP is an
*integration protocol* layered on top of this registry, not a replacement: an MCP
client wrapper would register remote tools here with the same schema/permission
model. Tool invocations support a human-in-the-loop ``requires_approval`` flag.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON-schema-ish
    handler: Callable[..., Any]
    requires_approval: bool = False  # human-in-the-loop denial capability (MCP-aligned)

    def schema(self) -> dict[str, Any]:
        """OpenAI/Gemini-style function schema for exposing to an LLM."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self._tools.values()]

    def invoke(self, name: str, *, approved: bool = False, **kwargs: Any) -> Any:
        tool = self.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool: {name}")
        if tool.requires_approval and not approved:
            raise PermissionError(f"Tool {name!r} requires human approval.")
        return tool.handler(**kwargs)


_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """Process-wide tool registry, populated with builtins on first access."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
        from app.ai.tools.builtins import register_builtins

        register_builtins(_registry)
    return _registry
