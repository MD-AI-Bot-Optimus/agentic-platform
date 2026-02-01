import pytest
from agentic_platform.workflow import engine
from agentic_platform.agents import base, artifact_store
from agentic_platform.audit import audit_log

class DummyToolClient:
    def call(self, tool_name, args):
        return {"result": f"ran {tool_name}"}

def test_agent_execution_in_workflow():
    # Setup workflow: start -> agent (tool) -> end
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "ocr_agent", "type": "tool", "tool": "ocr_tool"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "ocr_agent"},
            {"from": "ocr_agent", "to": "end"}
        ]
    }
    log = audit_log.InMemoryAuditLog()
    store = artifact_store.InMemoryArtifactStore()
    tool_client = DummyToolClient()
    agent = base.ToolCallingAgent(name="ocr_agent", version="v1", tool_client=tool_client)
    # Simulate workflow engine running agent node, storing output, and emitting audit
    result = engine.run(wf_def, input_artifact=None, tool_client=tool_client, audit_log=log)
    # Simulate agent output
    artifact = agent.run_tool("ocr_tool", {"foo": 1})
    ref = store.put(agent.name + ":" + agent.version, artifact)
    event = log.emit_event_with_artifact(agent, ref)
    # Check audit and artifact
    assert event.artifact_ref == ref
    assert store.get(ref) == artifact
    assert result["status"] == "completed"
