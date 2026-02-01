import pytest
from agentic_platform.adapters import n8n_adapter

def test_n8n_adapter_stub():
    adapter = n8n_adapter.N8NAdapter()
    with pytest.raises(NotImplementedError):
        adapter.call("some_tool", {"foo": "bar"})
