import pytest
from platform.audit import audit_log
from platform.core.types import AuditEvent

class DummyEvent(AuditEvent):
    pass

def test_audit_log_emits_start_and_end_events():
    log = audit_log.InMemoryAuditLog()
    start_event = AuditEvent(
        event_type="STEP_STARTED",
        job_id="job-1",
        node_id="node-1",
        timestamp="2026-01-31T00:00:00Z",
        status="started"
    )
    end_event = AuditEvent(
        event_type="STEP_ENDED",
        job_id="job-1",
        node_id="node-1",
        timestamp="2026-01-31T00:01:00Z",
        status="ended"
    )
    log.emit(start_event)
    log.emit(end_event)
    events = log.get_events(job_id="job-1")
    assert events[0].event_type == "STEP_STARTED"
    assert events[1].event_type == "STEP_ENDED"
    assert len(events) == 2
