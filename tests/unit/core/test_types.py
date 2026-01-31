import pytest
from agentic_platform.core import types

def test_artifact_ref():
    ref = types.ArtifactRef(id="artifact-123", type="pdf")
    assert ref.id == "artifact-123"
    assert ref.type == "pdf"

def test_tool_call():
    call = types.ToolCall(tool_name="ocr_page", args={"page": 1})
    assert call.tool_name == "ocr_page"
    assert call.args == {"page": 1}

def test_tool_result():
    result = types.ToolResult(success=True, output={"text": "hello"}, error=None)
    assert result.success is True
    assert result.output["text"] == "hello"
    assert result.error is None

def test_audit_event():
    event = types.AuditEvent(event_type="STEP_STARTED", job_id="job-1", node_id="node-1", timestamp="2026-01-31T00:00:00Z", status="started")
    assert event.event_type == "STEP_STARTED"
    assert event.job_id == "job-1"
    assert event.node_id == "node-1"
    assert event.timestamp == "2026-01-31T00:00:00Z"
    assert event.status == "started"


def test_artifact_ref_immutable():
    ref = types.ArtifactRef(id="artifact-immutable", type="txt")
    with pytest.raises(Exception):
        ref.id = "new-id"

def test_tool_call_args_empty():
    call = types.ToolCall(tool_name="noop", args={})
    assert call.args == {}

def test_tool_result_none_output():
    result = types.ToolResult(success=False, output=None, error="Some error")
    assert result.output is None
    assert result.error == "Some error"

def test_audit_event_equality_and_hash():
    event1 = types.AuditEvent(event_type="E", job_id="J", node_id="N", timestamp="T", status="S")
    event2 = types.AuditEvent(event_type="E", job_id="J", node_id="N", timestamp="T", status="S")
    assert event1 == event2
    assert hash(event1) == hash(event2)
