"""Unit tests for the tool registry."""

from __future__ import annotations

import pytest

from app.ai.tools.registry import Tool, ToolRegistry, get_registry


def test_builtins_registered():
    reg = get_registry()
    assert "word_count" in reg.names()
    assert "slugify" in reg.names()


def test_invoke_tool():
    reg = get_registry()
    result = reg.invoke("word_count", text="one two three")
    assert result["words"] == 3


def test_approval_required_tool_blocks_without_approval():
    reg = ToolRegistry()
    reg.register(
        Tool(
            name="danger",
            description="needs approval",
            parameters={"type": "object", "properties": {}},
            handler=lambda: "done",
            requires_approval=True,
        )
    )
    with pytest.raises(PermissionError):
        reg.invoke("danger")
    assert reg.invoke("danger", approved=True) == "done"
