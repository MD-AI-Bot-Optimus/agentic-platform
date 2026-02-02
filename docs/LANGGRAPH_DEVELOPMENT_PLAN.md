# LangGraph Development Plan (Phase 9)

**Status:** Planning | **Priority:** Critical | **Timeline:** 3-4 weeks | **Target Completion:** Late February 2026

---

## 📊 Executive Summary

Convert LangGraph adapter from **stub (simulates responses)** to **production-grade agent orchestration** with:
- Real LLM integration (Claude, GPT-4, Gemini)
- Persistent agent state and memory
- Tool use with automatic routing
- Iterative refinement loops
- Full test coverage

**Impact:** Unlock AI agent capabilities (agents decide which tools to call, iterate on results, learn from failures)

---

## 🎯 Phase 9 Goals

### Primary Goals
1. ✅ Add LangGraph + LangChain dependencies
2. ✅ Implement real LangGraph state machine
3. ✅ Integrate Claude/GPT-4/Gemini LLM providers
4. ✅ Build tool-use agent pattern (agent decides what to call)
5. ✅ Add agent memory (conversation history)
6. ✅ Implement iterative refinement (loops)
7. ✅ Full test coverage (25+ tests)
8. ✅ Update documentation

### Success Metrics
- 25+ unit & integration tests (all passing)
- Real LLM agent can use tools autonomously
- Agent maintains conversation history
- Can handle multi-step reasoning
- 95%+ test coverage for LangGraph module

---

## 📋 Phase 9 Breakdown (Weeks 1-4)

### Week 1: Setup & Dependencies

**Tasks:**
1. Add LangGraph dependencies to pyproject.toml
   - langgraph>=0.0.24
   - langchain>=0.1.0
   - langchain-anthropic (or langchain-openai)
   - langchain-google-vertexai
   
2. Add LLM API keys configuration
   - Environment variables for API keys
   - Support multiple providers (Anthropic, OpenAI, Google)
   - Safe credential handling

3. Create LangGraph state schema
   ```python
   from langgraph.graph import StateGraph
   from typing import Annotated, TypedDict
   
   class AgentState(TypedDict):
       messages: Annotated[list, ...]
       tool_results: list
       current_tool: str
       iteration_count: int
   ```

4. Set up local development LLM option (for testing without API calls)
   - Ollama or similar
   - Fallback simulated responses

**Deliverables:**
- [ ] pyproject.toml updated
- [ ] .env.example with API keys
- [ ] LangGraph state schema defined
- [ ] Setup documentation

---

### Week 2: Core LangGraph Implementation

**Tasks:**
1. Implement LangGraphAgent class
   ```python
   class LangGraphAgent:
       def __init__(self, model: str = "claude-3.5-sonnet")
       def execute(self, input: dict) -> dict
       def with_tools(self, tools: list) -> LangGraphAgent
       def with_memory(self, memory_backend: str) -> LangGraphAgent
   ```

2. Build agent executor with tool use
   - Agent nodes (LLM reasoning)
   - Tool nodes (execute tools)
   - Conditional routing (agent decides next step)
   - Max iterations (prevent infinite loops)

3. Implement tool binding
   - Convert ToolRegistry tools to LangChain tools
   - Add tool schemas
   - Handle tool execution

4. Add conversation memory
   - Store messages in memory
   - Retrieve context for next iterations
   - Optional: SQLite backend

**Deliverables:**
- [ ] LangGraphAgent class (functional)
- [ ] Agent state machine working
- [ ] Tool binding working
- [ ] Memory storage working

---

### Week 3: Testing & Refinement

**Tasks:**
1. Write comprehensive tests (25+ tests)
   - Unit tests for each component
   - Integration tests (agent + tools)
   - Multi-step reasoning tests
   - Error handling tests
   - Memory persistence tests

2. Create test fixtures
   - Mock LLM for deterministic testing
   - Sample workflows
   - Test tools

3. Performance testing
   - Response time benchmarks
   - Token usage tracking
   - Cost tracking

4. Documentation
   - Usage guide
   - Examples (OCR, summarization, analysis)
   - Troubleshooting

**Deliverables:**
- [ ] 25+ tests (all passing)
- [ ] 95%+ coverage for langgraph_adapter.py
- [ ] Usage documentation
- [ ] Example workflows

---

### Week 4: Integration & Deployment

**Tasks:**
1. Update API to use real LangGraph adapter
   - Make it selectable alongside MCP
   - Add adapter parameter to `/run-workflow/`

2. Update UI
   - Show adapter selection (MCP vs LangGraph)
   - Display agent reasoning steps
   - Show memory/conversation history

3. Update documentation
   - Phase 9 complete
   - LangGraph guide
   - API examples

4. Deploy to Cloud Run
   - Test with real LLM API
   - Monitor performance
   - Verify cost tracking

**Deliverables:**
- [ ] API updated with LangGraph support
- [ ] UI shows agent reasoning
- [ ] Deployed to production
- [ ] Documentation complete

---

## 🏗️ Implementation Details

### Module Structure
```
src/agentic_platform/
├── adapters/
│   ├── langgraph_adapter.py      ← Replace stub
│   ├── langgraph_agent.py        ← New: agent implementation
│   ├── langgraph_tools.py        ← New: tool binding
│   └── langgraph_memory.py       ← New: memory management
├── llm/
│   ├── __init__.py
│   ├── models.py                 ← Model registry (Claude, GPT-4, Gemini)
│   ├── anthropic_client.py       ← Claude integration
│   ├── openai_client.py          ← GPT-4 integration
│   └── google_client.py          ← Gemini integration
└── agents/
    ├── langgraph_agent_base.py   ← Base agent class
    └── reasoning_agent.py        ← Reasoning agent implementation
```

### Key Classes

**LangGraphAdapter** (replaces stub)
```python
class LangGraphAdapter:
    """Real LangGraph adapter for agent orchestration."""
    
    def __init__(
        self,
        model: str = "claude-3.5-sonnet",
        tools: list = None,
        memory_backend: str = "in-memory"
    ):
        self.model = model
        self.tools = tools or []
        self.memory = MemoryManager(backend=memory_backend)
        self.agent = self._build_agent()
    
    def call(self, tool_name: str, args: dict) -> dict:
        """Execute via LangGraph agent (with reasoning)."""
        # Agent uses LLM to reason about tool use
        return self.agent.execute({"tool": tool_name, "args": args})
    
    def with_reasoning(self, prompt: str) -> dict:
        """Execute with multi-step reasoning."""
        # Agent reasons through multiple steps
        return self.agent.reason(prompt)
```

**LangGraphAgent** (new)
```python
class LangGraphAgent:
    """Agent that uses LangGraph for orchestration."""
    
    def __init__(self, model: str, tools: list, memory):
        self.model = model
        self.tools = tools
        self.memory = memory
        self.graph = self._build_state_graph()
    
    def execute(self, input: dict) -> dict:
        """Execute agent workflow."""
        # 1. Add to memory
        # 2. Call LLM with tools available
        # 3. LLM decides tool to call
        # 4. Execute tool
        # 5. Feed result back to LLM
        # 6. Repeat until done or max iterations
        # 7. Return final result
```

### Dependencies to Add

```toml
[project]
dependencies = [
    # ... existing ...
    "langgraph>=0.0.24",
    "langchain>=0.1.0",
    "langchain-core>=0.1.0",
    "langchain-anthropic>=0.0.2",      # For Claude
    "langchain-openai>=0.0.2",         # For GPT-4
    "langchain-google-vertexai>=0.0.2", # For Gemini
]
```

---

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests** (12 tests)
   - Agent initialization
   - Tool binding
   - State transitions
   - Memory operations

2. **Integration Tests** (8 tests)
   - Full agent workflow
   - Multi-step reasoning
   - Tool use with memory
   - Error handling

3. **Mock LLM Tests** (5 tests)
   - Deterministic behavior
   - Reasoning verification
   - Tool selection

**Example Test:**
```python
def test_langgraph_agent_multi_step_reasoning():
    """Agent can reason through multiple steps."""
    agent = LangGraphAgent(
        model="mock",  # Use mock for deterministic testing
        tools=[google_vision_ocr, summarize_text],
        memory=InMemoryMemory()
    )
    
    result = agent.execute({
        "prompt": "Analyze this document and provide a summary",
        "document": "..."
    })
    
    assert result["status"] == "success"
    assert len(result["reasoning_steps"]) > 1
    assert result["final_output"] is not None
```

---

## 📊 Current vs. Target State

### Current (Stub)
- ✅ Simulates responses
- ❌ No real LLM integration
- ❌ No tool use
- ❌ No memory
- ❌ No reasoning

### Target (Production)
- ✅ Real LLM integration (Claude, GPT-4, Gemini)
- ✅ Autonomous tool use (agent decides)
- ✅ Persistent memory
- ✅ Multi-step reasoning
- ✅ Iterative refinement
- ✅ Full test coverage
- ✅ Production-grade error handling

---

## 🚀 Success Criteria

- [ ] All dependencies installed and working
- [ ] 25+ tests passing (unit + integration)
- [ ] 95%+ code coverage for LangGraph module
- [ ] Agent can autonomously use tools
- [ ] Agent remembers conversation history
- [ ] Multi-step reasoning works
- [ ] Deployed to Cloud Run
- [ ] Documentation complete
- [ ] Examples working end-to-end

---

## 📝 Known Challenges

1. **LLM API Costs** - Real LLM calls cost money
   - Solution: Mock LLM for testing, optional real API

2. **Tool Schema Mapping** - LangChain vs. our tool registry
   - Solution: Build adapter layer

3. **Memory Scalability** - Conversation history grows
   - Solution: Vector DB + summarization (Phase 10)

4. **State Management** - Complex orchestration
   - Solution: Use LangGraph's built-in state management

---

## 📈 Phase 9 Roadmap (Gantt)

```
Week 1: Setup & Dependencies      ████░░░░░░░░░░░░░░
Week 2: Core Implementation       ░░████░░░░░░░░░░░░
Week 3: Testing & Refinement      ░░░░████░░░░░░░░░░
Week 4: Integration & Deploy      ░░░░░░████░░░░░░░░
```

---

## 🔗 Related Documentation

- [Roadmap.md](roadmap.md) - Phase 8 complete, Phase 9 planned
- [TECH_STACK_ANALYSIS.md](../TECH_STACK_ANALYSIS.md) - LLM integration section
- [Adapters.md](adapters.md) - Current adapter patterns

---

## ✅ Next Steps

1. **Review this plan** - Ensure alignment with goals
2. **Add dependencies** - Update pyproject.toml
3. **Start Week 1** - Setup & configuration
4. **Create PR structure** - Development branch
5. **Begin implementation** - Start with agent class

Ready to begin? Let's start with Week 1! 🚀
