# Agentic Platform Roadmap: From Pilot to Enterprise SaaS

**Current Status:** Phase 8 Complete (Single-Tenant Pilot) | **Next Pivot:** Phase 9 (Multi-Tenancy)

## 📖 Executive Narrative

### The Vision
The Agentic Platform is evolving from a standalone workflow engine into a **Global Multi-Tenant SaaS**. Our goal is to host thousands of distinct "Organizations," each with their own isolated data, configuration, and AI resources, all running on a shared, scalable infrastructure.

### The Problem
Currently, the platform assumes a single identity (the deployment owner). Logic for "Who is asking?" is implicit. Configuration (API keys, DB URLs) is global. This works for a prototype but prevents us from serving multiple clients (Enterprises) on the same instance.

### The Solution: "Lowest Level" Multi-Tenancy
We are architecting multi-tenancy not as an afterthought, but as the **lowest level primitive** in the system. 
1.  **Identity First**: Every request, event, and background job must carry a verified `TenantContext`.
2.  **Dynamic Resolution**: Resources (Vector DBs, LLM Credentials) are no longer static global variables. They are resolved *just-in-time* based on the Tenant Context.
3.  **Logical Isolation**: Data is separated logically (Row-Level Security) before physical separation (Sharding), ensuring agility without compromising security.

---

## 🗺️ Strategic Phases

### Phase 1: The Foundation (Completed)
*   **Goal**: Prove the core tech (Workflows + MCP + OCR).
*   **Result**: A functional single-user system.
*   **Key Tech**: FastAPI, Google Vision, JSON-RPC MCP.

### Phase 2: Identity & Context (Current Focus)
*   **Goal**: Establish the "Tenant" as a first-class citizen.
*   **Architecture**:
    *   **Provider Pattern (ADR-011)**: All external integrations (OCR, Vector DB) are abstracted behind interfaces.
    *   **Integration Conduit**: A central `Factory` dynamically instantiates the correct provider (Mock vs Enterprise) based on the active `TenantContext`.
    *   `TenantContext`: Immutable context object flowing through the entire stack.
*   **Outcome**: The system behaves differently depending on *who* is calling it, even without a real database yet.

### Phase 3: Data Isolation & Persistence
*   **Goal**: Securely store data for multiple tenants.
*   **Architecture**:
    *   **PostgreSQL RLS**: Row-Level Security policies to enforce isolation at the database layer.
    *   **Artifact Store**: S3 buckets with `/{tenant_id}/` prefixes.
*   **Outcome**: Tenant A cannot access Tenant B's data, enforced by the storage engine.

### Phase 4: Scalable SaaS Resources
*   **Goal**: specialized infrastructure per tenant constraints.
*   **Architecture**:
    *   **Worker Queues**: High-priority queues for Premium tenants.
    *   **Rate Limits**: Per-tenant API quotas.
    *   **BYO-Key**: Tenants provide their own API keys for LLM providers.

---

## 🛠️ Detailed Implementation Plan (Phase 2)

### 1. Core Tenancy Context
*   Reference: `src/agentic_platform/core/tenancy.py`
*   Implements `contextvars` to hold current Tenant ID safely in async loops.

### 2. Factory Refactor
*   Reference: `src/agentic_platform/integrations/factory.py`
*   Updates dependency injection to accept `tenant_id`.
*   Example: `get_knowledge_base(tenant_id="acme_corp")` returns a specific Pinecone index, while `get_knowledge_base(tenant_id="startup_inc")` returns a local mock.

### 3. Middleware
*   Extracts `X-Tenant-ID` header from incoming REST requests.
*   Initializes the `TenantContext` for the request lifecycle.
