from agentic_platform.adapters import mcp_adapter

def test_mcp_adapter_real():
    adapter = mcp_adapter.MCPAdapter()
    result = adapter.call("some_tool", {"foo": "bar"})
    assert result["tool"] == "some_tool"
    assert result["args"] == {"foo": "bar"}
    assert result["status"] == "success"
    assert "MCP simulated response" in result["result"]
