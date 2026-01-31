import pytest
from agentic_platform.audit import audit_log
from agentic_platform.core.types import AuditEvent

def test_audit_events_are_immutable_and_correlated():
    log = audit_log.InMemoryAuditLog()
    event = AuditEvent(
        event_type="STEP_STARTED",
        job_id="job-2",
        node_id="node-2",
        timestamp="2026-01-31T00:00:00Z",
        status="started"
    )
    log.emit(event)
    events = log.get_events(job_id="job-2")
    assert len(events) == 1
    assert events[0].job_id == "job-2"
    assert events[0].status == "started"
    # Immutability test
    with pytest.raises(Exception):
        events[0].status = "changed"
    # Append-only test
    log.emit(event)
    assert len(log.get_events(job_id="job-2")) == 2
