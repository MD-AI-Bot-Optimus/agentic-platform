# ADR-007: Error Event Emission in Workflow Engine

## Status
Accepted

## Context
To ensure robust observability and traceability, the workflow engine must emit audit events not only for successful steps but also for failures. Previously, errors in tool calls resulted in missing audit events for failed nodes, making it difficult to diagnose issues and reconstruct execution history.

## Decision
The workflow engine now emits a `STEP_STARTED` event before every tool call and a `STEP_ERRORED` event if the tool call raises an exception. This ensures that all attempted steps are recorded in the audit log, regardless of outcome.

## Consequences
- Improves auditability and post-mortem analysis of workflow runs.
- Enables downstream systems to react to error events (e.g., alerting, retries).
- All integration tests for error handling and audit log coverage now pass.

## Related Milestones
- Integration test for error handling (2026-01-31)
- Engine emits STEP_ERRORED events (2026-01-31)
