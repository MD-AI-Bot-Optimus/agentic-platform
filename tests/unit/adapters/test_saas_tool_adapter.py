from agentic_platform.adapters import saas_tool_adapter

def test_saas_tool_adapter_real():
    adapter = saas_tool_adapter.SaaSToolAdapter()
    result = adapter.call("some_tool", {"foo": "bar"})
    assert result["tool"] == "some_tool"
    assert result["args"] == {"foo": "bar"}
    assert result["status"] == "success"
    assert "SaaS simulated response" in result["result"]
