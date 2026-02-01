from typing import List
from agentic_platform.core.types import AuditEvent

class InMemoryAuditLog:
    def __init__(self):
        self._events: List[AuditEvent] = []

    def emit(self, event: AuditEvent):
        self._events.append(event)

    def get_events(self, job_id: str) -> List[AuditEvent]:
        return [e for e in self._events if e.job_id == job_id]

    def emit_event_with_artifact(self, agent, artifact_ref):
        # Minimal event with agent and artifact linkage
        event = type('AuditEventWithArtifact', (object,), {})()
        event.event_type = "AGENT_OUTPUT"
        event.job_id = getattr(agent, 'job_id', 'job-1')
        event.node_id = getattr(agent, 'name', 'unknown')
        event.timestamp = "2026-01-31T00:00:00Z"
        event.status = "output"
        event.artifact_ref = artifact_ref
        event.agent_name = getattr(agent, 'name', None)
        event.agent_version = getattr(agent, 'version', None)
        self._events.append(event)
        return event
