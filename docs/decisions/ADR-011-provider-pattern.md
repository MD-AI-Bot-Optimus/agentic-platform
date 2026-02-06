# ADR-011: Enterprise Provider Pattern & Integration Conduits

## Context
As the Agentic Platform scales to support "Enterprise" tenants, we need a way to support custom integrations (e.g., private Vector DBs, proprietary OCR engines) without maintaining separate codebases for each client.

We need a standard pattern to:
1.  **Isolate** external dependencies behind stable interfaces.
2.  **Dynamically Swap** implementations based on the active `TenantContext`.
3.  **Stub** enterprise features for local development and testing.

## Decision
We will implement the **Provider Pattern** combined with a **Factory-based Conduit**.

### 1. The Provider Interface (Contract)
All external integrations must define an Abstract Base Class (ABC) in `src/agentic_platform/integrations/base.py`.
*   *Example*: `KnowledgeBaseProvider` determines *what* can be done (e.g., `search(query)`), not *how* it is done.

### 2. The Factory Conduit (Switchboard)
A central factory (`src/agentic_platform/integrations/factory.py`) acts as the conduit.
*   **Responsibility**: It is the *only* place allowed to instantiate concrete providers.
*   **Logic**: It reads the global `TenantContext` to decide which implementation to return.
*   *Snippet*:
    ```python
    def get_kb_provider():
        tenant = get_current_tenant()
        if tenant.is_enterprise:
            return EnterpriseKnowledgeBase(tenant.db_config)
        return MockKnowledgeBase()
    ```

### 3. The Implementation (Stub vs Real)
*   **Mock Implementation**: In-memory, fast, no deps. Used for `default` tenant and CI/CD.
*   **Enterprise Implementation**: The "Real" connector (e.g., Pinecone/Weaviate). Can be stubbed initially to simulate network conditions and data structures before the actual API integration is built.

## Consequences
### Positive
*   **Zero-Downtime Migration**: We can switch a tenant from "Mock" to "Real" just by changing their config in the Registry.
*   **Testability**: We can write tests against `MockProvider` and be confident functionality works, avoiding flaky external API calls in CI.
*   **Extensibility**: Adding a new backend (e.g., "Azure OCR") only requires adding a class and updating the Factory; consumer code (Workflow Engine) never changes.

### Negative
*   **Indirection**: Developers must look at the Factory to know *which* code is actually running.
*   **Interface Lowest Common Denominator**: The ABC might limit access to specific features of a provider (e.g., Pinecone specific metadata filters) unless we genericize them.
