import pytest
from agentic_platform.agents import base

class DummyToolClient:
    def call(self, tool_name, args):
        return {"result": f"ran {tool_name}"}

def test_base_agent_instantiation():
    agent = base.Agent(name="ocr", version="v1")
    assert agent.name == "ocr"
    assert agent.version == "v1"

def test_tool_calling_agent_calls_tool():
    tool_client = DummyToolClient()
    agent = base.ToolCallingAgent(name="ocr", version="v1", tool_client=tool_client)
    result = agent.run_tool("ocr_tool", {"foo": 1})
    assert result["result"] == "ran ocr_tool"
