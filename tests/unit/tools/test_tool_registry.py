import pytest
from platform.tools import tool_registry

def test_tool_registry_register_and_call():
    def echo_handler(args):
        return {"echo": args["msg"]}

    registry = tool_registry.ToolRegistry()
    registry.register_tool(
        name="echo",
        schema={"type": "object", "properties": {"msg": {"type": "string"}}, "required": ["msg"]},
        handler=echo_handler,
    )
    assert "echo" in registry.list_tools()
    result = registry.call("echo", {"msg": "hello"})
    assert result == {"echo": "hello"}

    # Test input validation (missing required field)
    with pytest.raises(Exception):
        registry.call("echo", {})
