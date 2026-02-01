import pytest
from agentic_platform.adapters import mcp_adapter

def test_mcp_adapter_stub():
    adapter = mcp_adapter.MCPAdapter()
    with pytest.raises(NotImplementedError):
        adapter.call("some_tool", {"foo": "bar"})
