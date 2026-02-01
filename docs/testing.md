# Testing Strategy

This document describes the testing philosophy, coverage goals, and practical approach for the Multi-AI Agentic Platform.

## Philosophy
- **TDD-First:** All features are developed test-first, with failing tests preceding implementation.
- **Red → Green → Refactor:** Each commit is a vertical slice that moves the codebase from failing to passing tests, then refactors for clarity and maintainability.
- **Mock Everything External:** All external systems (MCP, DB, SaaS, LangGraph, n8n) are mocked or abstracted behind interfaces until integration is required.

## Test Types
- **Unit Tests:**
  - Cover all core logic, domain types, and adapters
  - Use in-memory/fake implementations for all ports
  - Located in `tests/unit/`
- **Integration Tests:**
  - Validate contracts between modules and with real or stubbed adapters
  - Example: integration test for workflow engine with stubbed adapter and audit log
  - Example: integration test for branching workflow (conditional edges)
  - Located in `tests/integration/`
- **End-to-End (E2E) Tests:**
  - Planned for full workflow execution, including CLI and real integrations

## Coverage Goals
- 100% of core logic and interfaces covered by unit tests
- All adapters (MCP, LangGraph, n8n, etc.) must have integration tests
- All critical paths (workflow execution, tool calls, audit) must be exercised in tests

## Practical Approach
- Use `pytest` for all test discovery and execution
- Use `pytest` fixtures for setup/teardown and deterministic test data
- Use mocks/fakes for all external dependencies
- Add integration tests as new adapters are introduced
- Maintain milestone commits for all major test additions

## How to Run Tests
```sh
python -m pytest
```

## Continuous Integration
- (Planned) Add CI workflow to run all tests on push/PR
- Fail builds if any test fails or coverage drops below threshold

---

This strategy ensures the platform remains robust, refactorable, and integration-ready as it grows.
