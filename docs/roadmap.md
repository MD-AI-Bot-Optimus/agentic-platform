55. test: integration test for error handling (adapter failure, audit log error event)
54. test: integration test for branching workflow (conditional edges)
# Project Roadmap & TDD Commit History

This document details the incremental, test-driven development (TDD) roadmap for the Multi-AI Agentic Platform. Each milestone is a thin, vertical slice, with all external systems mocked until core contracts are stable.

## Phase 0 — Bootstrap + Red Tests
1. chore: init repo with pyproject, src layout, pytest
2. test: add failing test for JobId + CorrelationId generation
3. feat: add core id utilities
4. test: add failing tests for core domain types
5. feat: implement core domain dataclasses + validation

## Phase 1 — Audit Trail
6. test: audit log emits start/end events for a step
7. feat: in-memory audit log
8. test: audit events must be immutable + correlated
9. feat: audit event model + helpers
10. refactor: centralize audit event creation

## Phase 2 — Tool Interface + Mocking
11. test: tool registry can list and call tools
12. feat: tool protocol + tool registry
13. test: fake tool client simulates external tools deterministically
14. feat: implement FakeToolClient
15. test: tool call errors return structured error schema
16. feat: implement tool error schema + validation

## Phase 3 — Workflow Engine
17. test: parse workflow definition from YAML
18. feat: workflow definition parser + validator
19. test: engine executes single-node workflow
20. feat: workflow engine minimal runner
21. test: engine supports conditional branching
22. feat: implement branching conditions
23. test: engine retries node on transient failure
24. feat: implement retry policy
25. test: engine routes to human review when confidence below threshold
26. feat: add human-in-loop state + routing

## Phase 4 — Agents + Registry
27. test: agent registry registers versioned agents
28. feat: implement agent registry (in-memory)
29. test: agent node calls tool client and writes artifact
30. feat: implement artifact store (in-memory)
31. feat: implement base Agent and ToolCallingAgent
32. test: agent output is checksummed and versioned
33. feat: artifact hashing + audit linking
34. refactor: separate workflow node executor from engine


## Phase 5 — End-to-end MVP workflow
35. test: end-to-end OCR MVP happy path
36. feat: add OCR MVP workflow YAML
37. feat: add fake tool fixtures for OCR flow
38. test: end-to-end low-confidence route to human review
39. feat: implement review queue as state + artifact
40. test: review approval resumes workflow
41. feat: implement resume token + state hydration
42. chore: add CLI runner + JSON output

## Phase 5.5 — Model Selection
43. test: model selection per node/task (red)
44. feat: implement ModelRouter for routing tool calls to specific GPT/model
45. test: fallback/default model selection logic
46. docs: update architecture and usage for model selection

## Phase 6 — Prepare for Real Integrations
43. test: tool client interface can be swapped without changing engine
44. refactor: introduce ToolClient protocol
45. feat: add MCP adapter module (stubbed)
52. feat: implement minimal real MCP adapter (simulated response)
46. test: policy enforcement blocks unauthorized tool/model call
47. feat: implement tool/model allowlist policy (ToolAllowlistPolicy)
48. test: PII redaction in audit logs
49. feat: implement PII redaction middleware (PiiRedactor)
50. docs: ADR for tool contracts, audit, workflow DSL
51. test: integration test for workflow engine with stubbed adapter and audit log

---

For each phase, see the codebase and docs for detailed implementation and test coverage.
