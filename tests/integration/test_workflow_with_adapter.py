

from agentic_platform.workflow import engine
from agentic_platform.adapters import mcp_adapter
from agentic_platform.audit.audit_log import InMemoryAuditLog

class DummyMCPAdapter(mcp_adapter.MCPAdapter):
    def __init__(self):
        self.called = False
        self.last_tool = None
    def call(self, tool_name, args):
        self.called = True
        self.last_tool = tool_name
        return {"result": f"stubbed result for {tool_name}"}

def test_workflow_engine_with_adapter():
    # Minimal workflow: start -> tool -> end
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "step1", "type": "tool", "tool": "summarize", "model": "gpt-4"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "step1"},
            {"from": "step1", "to": "end"}
        ]
    }
    tool_client = DummyMCPAdapter()
    audit_log = InMemoryAuditLog()
    result = engine.run(wf_def, input_artifact={"text": "hello world"}, tool_client=tool_client, audit_log=audit_log)
    assert tool_client.called
    assert tool_client.last_tool == "summarize"
    # Check audit log events for step1
    events = audit_log.get_events("job-1")
    step1_events = [e for e in events if e.node_id == "step1"]
    assert any(e.event_type == "STEP_STARTED" for e in step1_events)
    assert any(e.event_type == "STEP_ENDED" for e in step1_events)
