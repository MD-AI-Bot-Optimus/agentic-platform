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

**Relevant code:**
- Example unit test: [tests/unit/workflow/test_engine.py](../../tests/unit/workflow/test_engine.py) demonstrates TDD for the workflow engine, with tests written before implementation and updated as features evolve.
- Example integration test: [tests/integration/test_api.py](../../tests/integration/test_api.py) shows end-to-end testing of the REST API, verifying that the system works as a whole and that new features are always covered by tests before being committed.

## Consequences
- High test coverage and confidence in changes.
- Easy to track progress and roll back if needed.
- Documentation and codebase remain in sync.

## Related Milestones
- All major features and integrations (2026-01)
- Roadmap and architecture docs (2026-01)
