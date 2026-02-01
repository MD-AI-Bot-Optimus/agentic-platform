## Adapter & Error Handling Coverage

- Integration tests verify that both the API and CLI support runtime adapter selection (MCP, LangGraph).
- See `tests/integration/test_api_adapter_selection.py` and `tests/integration/test_cli_adapter_selection.py` for examples.
- Additional integration tests cover error scenarios:
  - Invalid adapter selection (`test_api_invalid_adapter.py`)
  - Malformed workflow definition (`test_api_malformed_workflow.py`)
  - Missing input artifact (`test_api_missing_input.py`)
  - Adapter/tool error handling (`test_workflow_error_handling.py`)
## CLI Testing
You can run a workflow end-to-end from the command line:
```sh
PYTHONPATH=src .venv/bin/python src/agentic_platform/cli.py --workflow demo_workflow.yaml --input demo_input.json
```

# Testing Strategy (API & UI)

This document describes the testing philosophy, coverage goals, and practical approach for the Multi-AI Agentic Platform.

## Philosophy
- **TDD-First:** All features are developed test-first, with failing tests preceding implementation.
- **Red → Green → Refactor:** Each commit is a vertical slice that moves the codebase from failing to passing tests, then refactors for clarity and maintainability.
- **Mock Everything External:** All external systems (MCP, DB, SaaS, LangGraph, n8n) are mocked or abstracted behind interfaces until integration is required.

## Test Types
- **UI Tests:**
  - Cover all major UI flows (file upload, adapter selection, workflow run, error display)
  - Use React Testing Library and Jest (see `ui/App.test.jsx`)
  - Ensure UI is responsive and works on mobile/desktop
- **Unit Tests:**
  - Cover all core logic, domain types, and adapters
  - Use in-memory/fake implementations for all ports
  - Located in `tests/unit/`
- **Integration Tests:**
  - Validate contracts between modules and with real or stubbed adapters
  - Example: integration test for workflow engine with stubbed adapter and audit log
  - Example: integration test for branching workflow (conditional edges)
  - Example: integration test for error handling (adapter failure, audit log error event)
  - Example: integration test for artifact storage (S3 adapter, audit log linkage)
  - Located in `tests/integration/`
- **End-to-End (E2E) Tests:**
  - Planned for full workflow execution, including CLI and real integrations

- 100% of core logic and interfaces covered by unit tests
- All major UI flows covered by automated tests
- All adapters (MCP, LangGraph, n8n, etc.) must have integration tests
- All critical paths (workflow execution, tool calls, audit, error handling, invalid input) must be exercised in tests

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
