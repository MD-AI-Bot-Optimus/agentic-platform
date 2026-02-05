# How to Test Each Feature - Quick Reference

A quick lookup guide showing where to find tests for each core feature.

---

## 1️⃣ Pure LangGraph Implementation

**What it tests**: Graph compiles and executes without manual loops

**Test Location**: [test_stategraph_implementation.py](../tests/unit/phase_9/test_stategraph_implementation.py#L270-L310)

**Key Tests**:
```python
# Test file: test_stategraph_implementation.py
test_graph_compiles()              # ✅ Graph.compile() works
test_graph_has_nodes()             # ✅ Proper structure
test_graph_executes_basic_prompt() # ✅ Direct invocation
```

**Run**:
```bash
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestStateGraphCompilation -v
```

---

## 2️⃣ Tool Integration

**What it tests**: Tools detected, executed, results tracked

**Test Location**: [test_stategraph_implementation.py](../tests/unit/phase_9/test_stategraph_implementation.py#L90-L160)

**Key Tests**:
```python
# Test file: test_stategraph_implementation.py
test_tool_node_executes_tool()      # ✅ Tool.func() called
test_tool_node_adds_tool_result()   # ✅ Results in state
test_tool_node_returns_messages_update() # ✅ ToolMessage added
```

**Run**:
```bash
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestToolNodeImplementation -v
```

---

## 3️⃣ Intelligent Routing

**What it tests**: Router decides tool_node vs END correctly

**Test Location**: [test_stategraph_implementation.py](../tests/unit/phase_9/test_stategraph_implementation.py#L163-L210)

**Key Tests**:
```python
# Test file: test_stategraph_implementation.py
test_router_detects_tool_use()       # ✅ Routes to tool_node
test_router_detects_end_condition()  # ✅ Routes to END
test_router_respects_max_iterations() # ✅ Respects limits
```

**Run**:
```bash
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestRouterImplementation -v
```

---

## 4️⃣ Message Accumulation

**What it tests**: Full conversation history preserved

**Test Location**: [test_stategraph_implementation.py](../tests/unit/phase_9/test_stategraph_implementation.py#L246-L290)

**Key Tests**:
```python
# Test file: test_stategraph_implementation.py
test_state_accumulates_messages()          # ✅ Messages preserved
test_state_iteration_count_increases()     # ✅ Count tracked
test_state_tool_results_accumulate()       # ✅ Results added
```

**Run**:
```bash
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestStateFlowThroughGraph -v
```

---

## 5️⃣ Error Resilience

**What it tests**: Graceful error handling in all nodes

**Test Location**: [test_stategraph_implementation.py](../tests/unit/phase_9/test_stategraph_implementation.py#L306-L350)

**Key Tests**:
```python
# Test file: test_stategraph_implementation.py
test_agent_node_handles_llm_error()   # ✅ LLM failure handled
test_tool_node_handles_tool_error()   # ✅ Tool failure handled
```

**Also**: [test_execution_loop.py](../tests/unit/phase_9/test_execution_loop.py#L94-L115)
```python
test_execute_handles_llm_failure()  # ✅ Full execution resilience
```

**Run**:
```bash
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestGraphErrorHandling -v
pytest tests/unit/phase_9/test_execution_loop.py::TestExecutionEdgeCases::test_execute_handles_llm_failure -v
```

---

## 6️⃣ Memory Integration

**What it tests**: Reasoning steps and tool calls tracked

**Test Location**: [test_langgraph_agent.py](../tests/unit/phase_9/test_langgraph_agent.py#L180-L210)

**Key Tests**:
```python
# Test file: test_langgraph_agent.py
test_agent_adds_messages_to_memory()     # ✅ Messages tracked
test_agent_memory_context_retrieval()    # ✅ Context available
```

**Also**: [test_stategraph_implementation.py](../tests/unit/phase_9/test_stategraph_implementation.py#L211-L235)
```python
test_agent_tracks_tool_calls()  # ✅ Tool calls tracked
```

**Run**:
```bash
pytest tests/unit/phase_9/test_langgraph_agent.py::TestAgentMemoryIntegration -v
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestAgentStateManagement -v
```

---

## 7️⃣ State Isolation

**What it tests**: Each node independent, single responsibility

**Test Location**: Multiple test classes

**Key Tests**:
```python
# Test file: test_stategraph_implementation.py
test_agent_node_returns_state_update()  # ✅ agent_node isolated
test_tool_node_isolated_from_agent()    # ✅ tool_node isolated
test_router_independent_decision_logic() # ✅ router isolated
```

**Run**:
```bash
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestAgentNodeImplementation -v
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestToolNodeImplementation -v
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestRouterImplementation -v
```

---

## 8️⃣ Graph Compilation

**What it tests**: Graph is production-ready

**Test Location**: [test_stategraph_implementation.py](../tests/unit/phase_9/test_stategraph_implementation.py#L270-L310) + [test_execution_loop.py](../tests/unit/phase_9/test_execution_loop.py#L150-L175)

**Key Tests**:
```python
# Test file: test_stategraph_implementation.py
test_graph_compiles()  # ✅ Compiles successfully
test_graph_has_nodes() # ✅ Proper structure

# Test file: test_execution_loop.py
test_create_graph_returns_runnable()  # ✅ Ready to invoke
test_graph_invoke_with_initial_state() # ✅ Executes end-to-end
```

**Run**:
```bash
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestStateGraphCompilation -v
pytest tests/unit/phase_9/test_execution_loop.py::TestGraphExecution -v
```

---

## All Tests by File

### test_stategraph_implementation.py (24 tests)
- ✅ TestAgentNodeImplementation (6 tests)
- ✅ TestToolNodeImplementation (5 tests)
- ✅ TestRouterImplementation (5 tests)
- ✅ TestStateGraphCompilation (3 tests)
- ✅ TestStateFlowThroughGraph (3 tests)
- ✅ TestGraphErrorHandling (2 tests)

### test_execution_loop.py (24 tests)
- ✅ TestExecuteMethod (10 tests)
- ✅ TestToolIntegrationInExecution (3 tests)
- ✅ TestExecutionEdgeCases (5 tests)
- ✅ TestExecutionResult (4 tests)
- ✅ TestGraphExecution (2 tests)

### test_langgraph_agent.py (20 tests)
- ✅ TestLangGraphAgentInitialization (4 tests)
- ✅ TestLangGraphAgentBuilder (3 tests)
- ✅ TestAgentReasoningSteps (2 tests)
- ✅ TestAgentStateManagement (1 test)
- ✅ TestAgentMemoryIntegration (2 tests)
- ✅ TestAgentExecutionInterface (2 tests)
- ✅ TestAgentExecutionResult (2 tests)
- ✅ TestAgentConfigurationDefaults (2 tests)
- ✅ TestAgentIntegration (2 tests)

### Earlier test files (54 tests)
- ✅ test_dependencies.py (16 tests)
- ✅ test_agent_state.py (18 tests)
- ✅ test_llm_config.py (20 tests)

---

## Run All Tests

```bash
# All Phase 9 tests
pytest tests/unit/phase_9/ -v

# Just StateGraph tests
pytest tests/unit/phase_9/test_stategraph_implementation.py -v

# Just Execution tests
pytest tests/unit/phase_9/test_execution_loop.py -v

# Just Agent class tests
pytest tests/unit/phase_9/test_langgraph_agent.py -v

# With coverage
pytest tests/unit/phase_9/ --cov=src/agentic_platform/adapters/langgraph_agent --cov-report=html

# Just one feature
pytest tests/unit/phase_9/ -k "test_router" -v
```

---

## Understanding Test Organization

### By Component
- **agent_node** → TestAgentNodeImplementation (6 tests)
- **tool_node** → TestToolNodeImplementation (5 tests)
- **router** → TestRouterImplementation (5 tests)
- **create_graph** → TestStateGraphCompilation (3 tests)

### By Feature
- **Message accumulation** → TestStateFlowThroughGraph (3 tests)
- **Error handling** → TestGraphErrorHandling (2 tests)
- **Full execution** → TestExecuteMethod (10 tests)
- **Memory** → TestAgentMemoryIntegration (2 tests)

### By Test Type
- **Unit tests**: Individual node testing
- **Integration tests**: Nodes working together
- **End-to-end tests**: Full execute() method
- **Edge case tests**: Error, timeout, malformed input

---

## Example: Running Tests for One Feature

**Want to verify Tool Integration works?**

```bash
# Run all tool-related tests
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestToolNodeImplementation -v

# Output shows:
# test_tool_node_exists PASSED
# test_tool_node_takes_state PASSED
# test_tool_node_executes_tool PASSED ← Verifies execution
# test_tool_node_adds_tool_result PASSED ← Verifies tracking
# test_tool_node_returns_messages_update PASSED ← Verifies integration
```

---

## Debugging Failed Tests

If a test fails, use:

```bash
# Show full error details
pytest tests/unit/phase_9/test_stategraph_implementation.py::TestToolNodeImplementation::test_tool_node_executes_tool -vv

# Stop at first failure
pytest tests/unit/phase_9/ -x

# Drop into debugger on failure
pytest tests/unit/phase_9/ --pdb

# Show print statements during test
pytest tests/unit/phase_9/ -s
```

---

## Summary

| Feature | Tests | File | Classes |
|---------|-------|------|---------|
| Pure LangGraph | 3 | test_stategraph_implementation.py | TestStateGraphCompilation |
| Tool Integration | 5 | test_stategraph_implementation.py | TestToolNodeImplementation |
| Intelligent Routing | 5 | test_stategraph_implementation.py | TestRouterImplementation |
| Message Accumulation | 3 | test_stategraph_implementation.py | TestStateFlowThroughGraph |
| Error Resilience | 2+ | test_stategraph_implementation.py, test_execution_loop.py | TestGraphErrorHandling, TestExecutionEdgeCases |
| Memory Integration | 2+ | test_langgraph_agent.py, test_stategraph_implementation.py | TestAgentMemoryIntegration, TestAgentStateManagement |
| State Isolation | 8 | test_stategraph_implementation.py | Multiple classes |
| Graph Compilation | 5 | test_stategraph_implementation.py, test_execution_loop.py | TestStateGraphCompilation, TestGraphExecution |

**Total: 122 tests validating all 8 features** ✅
