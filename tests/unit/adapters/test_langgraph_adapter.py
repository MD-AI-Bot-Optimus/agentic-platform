import pytest
from agentic_platform.adapters import langgraph_adapter

import httpx
import pytest
from unittest.mock import patch

def test_langgraph_adapter_simulated():
    adapter = langgraph_adapter.LangGraphAdapter()
    result = adapter.call("some_tool", {"foo": "bar"})
    assert result["tool"] == "some_tool"
    assert result["args"] == {"foo": "bar"}
    assert result["status"] == "success"
    assert "LangGraph simulated response" in result["result"]

def test_langgraph_adapter_real_http():
    adapter = langgraph_adapter.LangGraphAdapter(config={"endpoint": "http://fake-endpoint"})
    with patch("httpx.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"tool": "some_tool", "args": {"foo": "bar"}, "result": "real", "status": "success"}
        result = adapter.call("some_tool", {"foo": "bar"})
        assert result["tool"] == "some_tool"
        assert result["args"] == {"foo": "bar"}
        assert result["status"] == "success"
        assert result["result"] == "real"
