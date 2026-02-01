57. feat: minimal CLI for running workflows from YAML/JSON
58. feat: minimal REST API for workflow execution (FastAPI)
56. test: integration test for artifact storage (S3 adapter, audit log linkage)
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
35. ✅ test: end-to-end OCR MVP happy path (COMPLETED)
36. ✅ feat: add OCR MVP workflow YAML (COMPLETED)
37. ✅ feat: add fake tool fixtures for OCR flow (COMPLETED)
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

## Phase 6 — Google Vision OCR Integration (COMPLETED)
✅ 60. test: OCR integration end-to-end (image upload, extraction, formatted output)
✅ 61. feat: GoogleVisionOCR adapter with Application Default Credentials (ADC)
✅ 62. feat: `/run-ocr/` FastAPI endpoint with multipart form support
✅ 63. feat: OCR workflow YAML (ocr_mvp.yaml) with nodes/edges format
✅ 64. feat: React OCR demo component with image upload and results display
✅ 65. feat: formatted text output with line-by-line display
✅ 66. docs: OCR architecture, authentication, and API usage
✅ 67. chore: Google Cloud SDK setup, ADC configuration, project setup

## Phase 7 — MCP Server Integration (COMPLETED)
✅ 68. test: MCPServer protocol implementation with 22 unit tests
✅ 69. feat: MCPServer JSON-RPC 2.0 handler (tools/list, tools/call methods)
✅ 70. feat: FastAPI /mcp/request and /mcp/tools endpoints
✅ 71. feat: MCPAdapter HTTP client for calling remote MCP servers
✅ 72. feat: ToolRegistry integration with MCPServer for tool discovery
✅ 73. test: MCPAdapter client tests with 22 unit tests
✅ 74. test: End-to-end MCP workflow with 13 integration tests
✅ 75. test: OCR tool calling via MCP protocol
✅ 76. feat: React MCP Tool Tester UI component (tool selection, arg input, result display)
✅ 77. feat: Tool discovery from /mcp/tools endpoint
✅ 78. docs: ADR-010 for MCP Server Integration decision record
✅ 79. docs: Comprehensive MCP Implementation Guide (mcp-guide.md)
✅ 80. docs: API documentation with MCP endpoint examples
✅ 81. chore: All 57 MCP tests passing (22 MCPServer + 22 MCPAdapter + 13 E2E)

## Phase 7.5 — UI Polish & Documentation (COMPLETED)
✅ 82. feat: Restructure UI cards into 2-column responsive grid layout
✅ 83. feat: Add Highway 1 Pacific Coast background image
✅ 84. feat: Fixed sticky header that doesn't scroll beyond
✅ 85. feat: Improved card styling with shadows and borders
✅ 86. chore: Remove unused CSS and SVG files
✅ 87. docs: Update main README with current status and features
✅ 88. docs: Update UI README with component descriptions and guide
✅ 89. docs: Update roadmap with Phase 7.5 completion
✅ 90. docs: Add sample data for OCR testing (handwriting, letter, images)

---

For each phase, see the codebase and docs for detailed implementation and test coverage.
