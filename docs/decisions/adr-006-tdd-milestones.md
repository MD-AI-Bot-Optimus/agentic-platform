# ADR-006: Test-Driven, Milestone-Driven Development

## Status
Accepted

## Context
To ensure reliability, maintainability, and safe evolution of the platform, all features are developed using a test-driven, milestone-driven approach. Each vertical slice is committed with passing tests and updated documentation.

## Decision
- All new features begin with a failing (red) test.
- Implementation proceeds until the test passes (green).
- Each milestone is committed with code, tests, and docs.
- Documentation (README, roadmap, ADRs) is updated at each milestone.

## Consequences
- High test coverage and confidence in changes.
- Easy to track progress and roll back if needed.
- Documentation and codebase remain in sync.

## Related Milestones
- All major features and integrations (2026-01)
- Roadmap and architecture docs (2026-01)
