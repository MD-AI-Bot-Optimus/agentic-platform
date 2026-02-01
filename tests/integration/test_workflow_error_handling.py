from agentic_platform.workflow import engine
from agentic_platform.audit.audit_log import InMemoryAuditLog

class FailingAdapter:
    def call(self, tool_name, args):
        raise RuntimeError(f"Simulated failure in {tool_name}")

def test_workflow_engine_error_handling():
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
    tool_client = FailingAdapter()
    audit_log = InMemoryAuditLog()
    try:
        engine.run(wf_def, input_artifact={"text": "fail"}, tool_client=tool_client, audit_log=audit_log)
    except RuntimeError as e:
        assert "Simulated failure" in str(e)
    else:
        assert False, "Expected RuntimeError was not raised"
    # Check audit log for error event
    events = audit_log.get_events("job-1")
    step1_events = [e for e in events if e.node_id == "step1"]
    assert any(e.event_type == "STEP_STARTED" for e in step1_events)
    assert any(e.event_type == "STEP_ERRORED" for e in step1_events)
