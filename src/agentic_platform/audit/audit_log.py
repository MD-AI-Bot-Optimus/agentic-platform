from typing import List
from agentic_platform.core.types import AuditEvent

class InMemoryAuditLog:
    def __init__(self):
        self._events: List[AuditEvent] = []

    def emit(self, event: AuditEvent):
        self._events.append(event)

    def get_events(self, job_id: str) -> List[AuditEvent]:
        return [e for e in self._events if e.job_id == job_id]
