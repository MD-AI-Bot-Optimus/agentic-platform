# ADR-002: Artifact Hashing and Versioning

## Status
Accepted

## Context
To support reproducibility, traceability, and efficient storage, all workflow artifacts must be versioned and content-addressed using cryptographic hashes.

## Decision
Artifacts produced by agents or tools are hashed (e.g., SHA-256) and stored with their hash as a unique reference. The artifact store supports versioning and linking artifacts to audit events.

## Consequences
- Enables deduplication and efficient artifact retrieval.
- Supports reproducibility and traceability of workflow runs.
- Audit log can reference artifacts by hash for integrity.

## Related Milestones
- InMemoryArtifactStore (2026-01-22)
- Artifact hashing and audit linking (2026-01-22)
