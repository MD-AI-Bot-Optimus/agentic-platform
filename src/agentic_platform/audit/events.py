from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    job_id: str
    node_id: str
    timestamp: str
    status: str
    details: Optional[Dict[str, Any]] = None

# Event types
STEP_STARTED = "STEP_STARTED"
STEP_ENDED = "STEP_ENDED"
# Add more as needed

def build_event(event_type: str, job_id: str, node_id: str, timestamp: str, status: str, details: Optional[Dict[str, Any]] = None) -> AuditEvent:
    return AuditEvent(
        event_type=event_type,
        job_id=job_id,
        node_id=node_id,
        timestamp=timestamp,
        status=status,
        details=details,
    )
