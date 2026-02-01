# ADR-001: Immutable Audit Log Events

## Status
Accepted

## Context
Auditability and traceability are critical for the platform. Audit log events must be immutable to ensure a reliable, tamper-evident record of all workflow and agent actions.

## Decision
All audit log events are implemented as immutable data structures. Once emitted, an event cannot be modified. The in-memory audit log enforces this by storing only frozen dataclasses or equivalent immutable types.

**Relevant code:**
- The `InMemoryAuditLog` class in [src/agentic_platform/audit/audit_log.py](../../src/agentic_platform/audit/audit_log.py) enforces immutability by storing only frozen dataclasses for audit events. All event emission and retrieval logic is implemented here.
- The audit event dataclasses (e.g., `AuditEvent`, `StepStartedEvent`, `StepCompletedEvent`) are defined as frozen dataclasses in [src/agentic_platform/core/types.py](../../src/agentic_platform/core/types.py), ensuring events cannot be mutated after creation.

## Consequences
- Ensures audit trail integrity and compliance.
- Prevents accidental or malicious modification of audit history.
- Requires careful design of event emission and storage APIs.

## Related Milestones
- InMemoryAuditLog (2026-01-20)
- Immutable audit event dataclasses (2026-01-20)
