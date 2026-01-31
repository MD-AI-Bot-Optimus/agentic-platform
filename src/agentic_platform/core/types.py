from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class ArtifactRef:
    id: str
    type: str

@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    args: Dict[str, Any]

@dataclass(frozen=True)
class ToolResult:
    success: bool
    output: Optional[Dict[str, Any]]
    error: Optional[Any]

@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    job_id: str
    node_id: str
    timestamp: str
    status: str
