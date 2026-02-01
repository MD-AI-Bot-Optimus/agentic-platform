import pytest
from agentic_platform.workflow import engine, definition
from agentic_platform.audit import audit_log
from agentic_platform.core.types import AuditEvent

class DummyToolClient:
    def call(self, tool_name, args):
        return {"result": f"ran {tool_name}"}

def test_engine_runs_single_node_workflow_and_emits_audit():
    # Minimal workflow definition: start -> tool -> end
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "tool1", "type": "tool", "tool": "dummy_tool"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "tool1"},
            {"from": "tool1", "to": "end"}
        ]
    }
    log = audit_log.InMemoryAuditLog()
    tool_client = DummyToolClient()
    # This will fail until engine is implemented
    result = engine.run(wf_def, input_artifact=None, tool_client=tool_client, audit_log=log)
    events = log.get_events(job_id=result["job_id"])
    assert any(e.event_type == "STEP_STARTED" for e in events)
    assert any(e.event_type == "STEP_ENDED" for e in events)
    assert result["status"] == "completed"

def test_engine_conditional_branching():
    """Engine should follow conditional branches based on input and emit correct audit events."""
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "tool1", "type": "tool", "tool": "dummy_tool1"},
            {"id": "tool2", "type": "tool", "tool": "dummy_tool2"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "tool1", "condition": "input == 'A'"},
            {"from": "start", "to": "tool2", "condition": "input == 'B'"},
            {"from": "tool1", "to": "end"},
            {"from": "tool2", "to": "end"}
        ]
    }
    log = audit_log.InMemoryAuditLog()
    tool_client = DummyToolClient()
    # Should take the branch based on input_artifact value
    result = engine.run(wf_def, input_artifact="A", tool_client=tool_client, audit_log=log)
    events = log.get_events(job_id=result["job_id"])
    # Should have run tool1, not tool2
    tool1_events = [e for e in events if getattr(e, "node_id", None) == "tool1"]
    tool2_events = [e for e in events if getattr(e, "node_id", None) == "tool2"]
    assert tool1_events, "tool1 should have events when input is 'A'"
    assert not tool2_events, "tool2 should not have events when input is 'A'"
    assert result["status"] == "completed"
    # Should fail until branching is implemented
    # Now test for input 'B'
    log2 = audit_log.InMemoryAuditLog()
    result2 = engine.run(wf_def, input_artifact="B", tool_client=tool_client, audit_log=log2)
    events2 = log2.get_events(job_id=result2["job_id"])
    tool1_events2 = [e for e in events2 if getattr(e, "node_id", None) == "tool1"]
    tool2_events2 = [e for e in events2 if getattr(e, "node_id", None) == "tool2"]
    assert not tool1_events2, "tool1 should not have events when input is 'B'"
    assert tool2_events2, "tool2 should have events when input is 'B'"
    assert result2["status"] == "completed"

def test_engine_multiple_tools_sequential():
    """Engine should execute multiple tool nodes in sequence and emit audit events for each."""
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "tool1", "type": "tool", "tool": "dummy_tool1"},
            {"id": "tool2", "type": "tool", "tool": "dummy_tool2"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "tool1"},
            {"from": "tool1", "to": "tool2"},
            {"from": "tool2", "to": "end"}
        ]
    }
    log = audit_log.InMemoryAuditLog()
    tool_client = DummyToolClient()
    result = engine.run(wf_def, input_artifact=None, tool_client=tool_client, audit_log=log)
    events = log.get_events(job_id=result["job_id"])
    tool1_events = [e for e in events if getattr(e, "node_id", None) == "tool1"]
    tool2_events = [e for e in events if getattr(e, "node_id", None) == "tool2"]
    assert tool1_events, "tool1 should have events"
    assert tool2_events, "tool2 should have events"
    assert result["status"] == "completed"

def test_engine_handles_no_valid_branch():
    """Engine should raise an error if no valid outgoing edge matches the input condition."""
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "tool1", "type": "tool", "tool": "dummy_tool1"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "tool1", "condition": "input == 'A'"},
            {"from": "tool1", "to": "end"}
        ]
    }
    log = audit_log.InMemoryAuditLog()
    tool_client = DummyToolClient()
    with pytest.raises(RuntimeError):
        engine.run(wf_def, input_artifact="B", tool_client=tool_client, audit_log=log)

def test_engine_unconditional_and_conditional_edges():
    """Engine should prefer conditional edge if condition matches, else take unconditional edge."""
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "toolA", "type": "tool", "tool": "dummy_toolA"},
            {"id": "toolB", "type": "tool", "tool": "dummy_toolB"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "toolA", "condition": "input == 'A'"},
            {"from": "start", "to": "toolB"},  # unconditional
            {"from": "toolA", "to": "end"},
            {"from": "toolB", "to": "end"}
        ]
    }
    log = audit_log.InMemoryAuditLog()
    tool_client = DummyToolClient()
    # Should take conditional edge to toolA
    result = engine.run(wf_def, input_artifact="A", tool_client=tool_client, audit_log=log)
    events = log.get_events(job_id=result["job_id"])
    toolA_events = [e for e in events if getattr(e, "node_id", None) == "toolA"]
    toolB_events = [e for e in events if getattr(e, "node_id", None) == "toolB"]
    assert toolA_events, "toolA should have events when input is 'A'"
    assert not toolB_events, "toolB should not have events when input is 'A'"
    # Should take unconditional edge to toolB
    log2 = audit_log.InMemoryAuditLog()
    result2 = engine.run(wf_def, input_artifact="C", tool_client=tool_client, audit_log=log2)
    events2 = log2.get_events(job_id=result2["job_id"])
    toolA_events2 = [e for e in events2 if getattr(e, "node_id", None) == "toolA"]
    toolB_events2 = [e for e in events2 if getattr(e, "node_id", None) == "toolB"]
    assert not toolA_events2, "toolA should not have events when input is 'C'"
    assert toolB_events2, "toolB should have events when input is not 'A'"
    assert result["status"] == "completed"
    assert result2["status"] == "completed"

def test_engine_handles_cycle_detection():
    """Engine should raise an error if a cycle is detected (infinite loop protection)."""
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "tool1", "type": "tool", "tool": "dummy_tool1"}
        ],
        "edges": [
            {"from": "start", "to": "tool1"},
            {"from": "tool1", "to": "start"}  # cycle
        ]
    }
    log = audit_log.InMemoryAuditLog()
    tool_client = DummyToolClient()
    with pytest.raises(RuntimeError):
        engine.run(wf_def, input_artifact=None, tool_client=tool_client, audit_log=log)

def test_engine_persistence_save_and_resume():
    """Engine should be able to save state mid-execution and resume from that state."""
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "tool1", "type": "tool", "tool": "dummy_tool1"},
            {"id": "tool2", "type": "tool", "tool": "dummy_tool2"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "tool1"},
            {"from": "tool1", "to": "tool2"},
            {"from": "tool2", "to": "end"}
        ]
    }
    log = audit_log.InMemoryAuditLog()
    tool_client = DummyToolClient()
    # Simulate running up to tool1, then save state
    # (Assume engine.run returns state if asked, and can resume from state)
    result, state = engine.run(wf_def, input_artifact=None, tool_client=tool_client, audit_log=log, stop_at_node="tool2", return_state=True)
    assert state is not None, "Engine should return intermediate state"
    # Now resume from saved state
    result2, _ = engine.run(wf_def, input_artifact=None, tool_client=tool_client, audit_log=log, resume_state=state)
    assert result2["status"] == "completed"
    events = log.get_events(job_id=result2["job_id"])
    tool2_events = [e for e in events if getattr(e, "node_id", None) == "tool2"]
    assert tool2_events, "tool2 should have events after resume"
