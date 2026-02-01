from agentic_platform.workflow import engine
from agentic_platform.adapters import mcp_adapter
from agentic_platform.audit.audit_log import InMemoryAuditLog

def test_workflow_engine_branching():
    # Workflow: start -> (branch) -> step1 or step2 -> end
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "step1", "type": "tool", "tool": "summarize", "model": "gpt-4"},
            {"id": "step2", "type": "tool", "tool": "translate", "model": "gpt-4"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "step1", "condition": "input['lang'] == 'en'"},
            {"from": "start", "to": "step2", "condition": "input['lang'] == 'fr'"},
            {"from": "step1", "to": "end"},
            {"from": "step2", "to": "end"}
        ]
    }
    tool_client = mcp_adapter.MCPAdapter()
    audit_log = InMemoryAuditLog()
    # English branch
    result_en = engine.run(wf_def, input_artifact={"lang": "en"}, tool_client=tool_client, audit_log=audit_log)
    events_en = audit_log.get_events("job-1")
    assert any(e.node_id == "step1" for e in events_en)
    assert not any(e.node_id == "step2" for e in events_en)
    # French branch
    audit_log = InMemoryAuditLog()
    result_fr = engine.run(wf_def, input_artifact={"lang": "fr"}, tool_client=tool_client, audit_log=audit_log)
    events_fr = audit_log.get_events("job-1")
    assert any(e.node_id == "step2" for e in events_fr)
    assert not any(e.node_id == "step1" for e in events_fr)
