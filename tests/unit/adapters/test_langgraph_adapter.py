import pytest
from agentic_platform.adapters import langgraph_adapter

def test_langgraph_adapter_stub():
    adapter = langgraph_adapter.LangGraphAdapter()
    with pytest.raises(NotImplementedError):
        adapter.call("some_tool", {"foo": "bar"})
