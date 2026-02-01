# Integration Plan: MCP, LangGraph, n8n

This document details how the platform will incorporate real-world integrations as it matures, while keeping the core logic stable, testable, and decoupled from external systems.

## 1. MCP (Model Context Protocol)
- **Adapter Pattern:** Implement `MCPToolClient` that conforms to the `ToolClient` interface.
- **Swappable:** The workflow engine and agents use the interface, so switching from `FakeToolClient` to `MCPToolClient` is a config change, not a rewrite.
- **Testing:** Continue to use the fake client in tests; add integration tests for MCP as needed.
- **Isolation:** MCP-specific logic is isolated in its adapter, keeping the rest of the platform agnostic.
- **Security:** Ensure authentication, authorization, and audit are preserved when calling MCP.

## 2. LangGraph
- **Graph Execution Engine:** Introduce a `LangGraphEngine` that implements the workflow engine interface.
- **Incremental Adoption:** Start by running simple workflows through LangGraph, then expand to more complex agent graphs.
- **Compatibility:** Maintain the current in-memory engine for tests and local dev; LangGraph is an optional backend.
- **Extensibility:** Add support for LangGraph-specific features (e.g., advanced branching, retries) via configuration and node metadata.
- **Observability:** Ensure audit and traceability are preserved when using LangGraph.

## 3. n8n (Workflow Automation)
- **Orchestration Layer:** Expose platform workflows as n8n nodes or trigger n8n flows from within the platform.
- **API Contracts:** Define clear REST/gRPC contracts for workflow execution and artifact management.
- **Integration Points:**
  - n8n can trigger platform workflows via API
  - Platform can emit events or call n8n for external automation
- **Security & Observability:** Ensure audit and traceability are preserved across boundaries.

## General Integration Principles
- **Adapters, Not Rewrites:** All integrations are added as new modules/classes that implement existing interfaces.
- **Test Coverage:** Maintain high test coverage with mocks; add integration tests for each adapter.
- **Configurable:** Use dependency injection or config files to select which implementation (fake, in-memory, MCP, LangGraph, n8n) is active.
- **Documentation:** Each integration will be documented in `docs/decisions/` and the README as it is added.

## Example Roadmap for Integration
1. Add `MCPToolClient` and integration tests (keep FakeToolClient as default for tests)
2. Add `LangGraphEngine` and allow switching engines via config
3. Add n8n API endpoints and/or n8n node definitions
4. Document integration patterns and update ADRs

---

This plan ensures the platform is integration-ready, with all progress and integration steps milestone-driven and documented.
