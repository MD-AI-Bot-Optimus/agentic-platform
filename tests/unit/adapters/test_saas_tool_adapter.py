import pytest
from agentic_platform.adapters import saas_tool_adapter

def test_saas_tool_adapter_stub():
    adapter = saas_tool_adapter.SaaSToolAdapter()
    with pytest.raises(NotImplementedError):
        adapter.call("some_tool", {"foo": "bar"})
