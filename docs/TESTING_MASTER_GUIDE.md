# Agentic Platform: Testing Master Guide

> **Scope**: Testing Philosophy, Quick Reference, and Detailed Feature Guide.
> **Related**: [UI_TEST_PLAN.md](UI_TEST_PLAN.md) (Browser/System Tests), [OCR_RECOVERY_REPORT.md](OCR_RECOVERY_REPORT.md) (Recent Feature Verification).

---

## 1. Testing Philosophy
- **TDD-First**: Features are developed test-first. Fails → Pass → Refactor.
- **Mock Externalities**: We mock LLMs, DBs, and APIs in unit tests to ensure speed and stability.
- **Vertical Slices**: Tests cover the "happy path" end-to-end (Unit -> Integration -> UI).
- **Run Often**: `python -m pytest` is the heartbeat of development.

---

## 2. Quick Reference (Cheat Sheet)

### Common Commands
```bash
# Run All Tests
pytest

# Run Specific Phase (e.g., Phase 9)
pytest tests/unit/phase_9/ -v

# Run a Single Test File
pytest tests/unit/phase_9/test_stategraph_implementation.py -v

# Run with Coverage
pytest --cov=src/agentic_platform

# Debug on Failure (drops into pdb)
pytest --pdb
```

### Key Test Locations
| Component | Test Path |
|-----------|-----------|
| **Agent Logic** | `tests/unit/phase_9/test_langgraph_agent.py` |
| **StateGraph** | `tests/unit/phase_9/test_stategraph_implementation.py` |
| **Execution Loop** | `tests/unit/phase_9/test_execution_loop.py` |
| **API** | `tests/integration/test_api_*.py` |
| **UI** | `ui/App.test.jsx` (Jest) |

---

## 3. Detailed Feature Testing Guide

### A. Pure LangGraph Implementation
**Goal**: Verify the graph compiles and executes without manual loops.
- **File**: `test_stategraph_implementation.py`
- **Key Test**: `test_graph_compiles()` validates that `create_graph()` returns a compiled `StateGraph` object that is callable.

### B. Intelligent Routing
**Goal**: Verify the agent properly chooses between Tools and Final Answer.
- **File**: `test_stategraph_implementation.py`
- **Key Tests**:
    - `test_router_detects_tool_use()`: Ensures presence of "tool_use" string routes to `tool_node`.
    - `test_router_detects_end_condition()`: Ensures normal text routes to `__end__`.
    - `test_router_respects_max_iterations()`: Failsafe check.

### C. Tool Integration
**Goal**: Verify tools are detected, executed, and results are tracked.
- **File**: `test_stategraph_implementation.py`
- **Key Test**: `test_tool_node_executes_tool()` mocks a tool function and asserts it was called with correct arguments from the state.

### D. Memory & State Accumulation
**Goal**: Verify the conversation history is preserved.
- **File**: `test_stategraph_implementation.py`
- **Key Test**: `test_state_accumulates_messages()` checks that the list of messages grows with each iteration and preserves the original inputs.

### E. Error Resilience
**Goal**: Verify the agent doesn't crash on bad inputs or API failures.
- **File**: `test_execution_loop.py`
- **Key Test**: `test_execute_handles_llm_failure()` forces a mock exception and asserts the agent returns a valid result object with status `error` (not crashing).

---

## 4. Debugging Guide (VS Code)
To see the graph in action step-by-step:
1.  Open `src/agentic_platform/adapters/langgraph_agent.py`.
2.  Set a breakpoint in `router()` or `agent_node()`.
3.  Run the **"Python: Debug Test"** configuration.
4.  Inspect `state["messages"]` to see the conversation flow.

---

## 5. UI & System Testing
For browser-based verification flows (OCR, Agent Tab, Workflow Editor), refer to **[UI_TEST_PLAN.md](UI_TEST_PLAN.md)**.
