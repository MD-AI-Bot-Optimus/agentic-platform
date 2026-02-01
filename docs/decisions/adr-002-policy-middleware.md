# ADR-002: Policy Enforcement Middleware

## Status
Accepted

## Context
The platform must support enforcement of security and compliance policies, such as tool/model allowlists and PII redaction, without entangling these concerns with core workflow or agent logic.

## Decision
Policy enforcement is implemented as middleware or utility classes (e.g., `ToolAllowlistPolicy`, `PiiRedactor`) that can be composed into the workflow engine, audit log, or agent execution pipeline. These are tested independently and can be extended for additional policies.

## Consequences
- Security and compliance logic is isolated from core workflow/agent code.
- Policies can be tested, swapped, or extended independently.
- Middleware can be applied at multiple points (e.g., before tool call, before audit log emit).

## Related Milestones
- ToolAllowlistPolicy (2026-01-31)
- PiiRedactor (2026-01-31)
