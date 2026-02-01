# ADR-009: Modern Monorepo with React UI and FastAPI Backend

## Status
Accepted

## Context
The Agentic Platform project now includes both a modern React (Material UI) frontend and a FastAPI backend in a single monorepo. This structure is common in enterprise projects for small to medium teams, enabling:
- Easier coordination between frontend and backend
- Shared documentation, tests, and CI/CD
- Simplified onboarding and local development

## Decision
- Keep both UI and backend in a single repository
- Use Material UI for a modern, responsive frontend
- Use FastAPI for the backend API
- Provide a single startup script for both services
- Maintain unified documentation and test strategy

## Consequences
- Faster iteration and easier integration
- Unified test and deployment pipelines
- Easy to split into separate repos in the future if needed

---

See README.md and docs/ for updated setup, testing, and architecture details.
