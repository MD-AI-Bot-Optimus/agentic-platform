from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import List, Optional
import time

@dataclass
class TraceStep:
    layer: str  # e.g., "Tenant", "Factory", "Tool"
    message: str
    detail: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class TraceData:
    steps: List[TraceStep] = field(default_factory=list)

    def add_step(self, layer: str, message: str, detail: Optional[str] = None):
        self.steps.append(TraceStep(layer, message, detail))
    
    def to_dict(self):
        return [
            {
                "layer": s.layer,
                "message": s.message,
                "detail": s.detail,
                "timestamp": s.timestamp
            }
            for s in self.steps
        ]

_trace_context: ContextVar[Optional[TraceData]] = ContextVar("trace_context", default=None)

def init_trace():
    """Initialize a new trace for the current context."""
    return _trace_context.set(TraceData())

def get_trace() -> Optional[TraceData]:
    """Get the current trace data."""
    return _trace_context.get()

def add_trace_step(layer: str, message: str, detail: Optional[str] = None):
    """Add a step to the current trace, if active."""
    trace = get_trace()
    if trace:
        trace.add_step(layer, message, detail)
