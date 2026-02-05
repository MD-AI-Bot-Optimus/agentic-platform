"""
Phase 9: Verify LangGraph dependencies are installed and working.

Tests:
- LangGraph package imports
- LangChain integration
- LLM provider factory
- Mock LLM functionality
"""

import pytest
import sys


class TestLangGraphDependencies:
    """Verify LangGraph packages are installed."""
    
    def test_langgraph_import(self):
        """LangGraph package should be importable."""
        try:
            import langgraph
            assert langgraph is not None
        except ImportError as e:
            pytest.fail(f"langgraph not installed: {e}")
    
    def test_langchain_import(self):
        """LangChain package should be importable."""
        try:
            import langchain
            assert langchain is not None
        except ImportError as e:
            pytest.fail(f"langchain not installed: {e}")
    
    def test_langchain_core_import(self):
        """LangChain core should be importable."""
        try:
            from langchain_core.messages import BaseMessage, HumanMessage
            assert BaseMessage is not None
            assert HumanMessage is not None
        except ImportError as e:
            pytest.fail(f"langchain-core not installed: {e}")
    
    def test_stategraph_import(self):
        """StateGraph should be importable from langgraph."""
        try:
            from langgraph.graph import StateGraph
            assert StateGraph is not None
        except ImportError as e:
            pytest.fail(f"StateGraph import failed: {e}")


class TestLLMProviderFactory:
    """Test LLM provider factory."""
    
    def test_llm_provider_enum_exists(self):
        """LLMProvider enum should exist."""
        from agentic_platform.llm import LLMProvider
        assert hasattr(LLMProvider, "ANTHROPIC")
        assert hasattr(LLMProvider, "OPENAI")
        assert hasattr(LLMProvider, "GOOGLE")
        assert hasattr(LLMProvider, "MOCK")
    
    def test_get_llm_model_mock(self):
        """Should be able to get mock LLM."""
        from agentic_platform.llm import get_llm_model
        from langchain_core.messages import AIMessage
        llm = get_llm_model(provider="mock")
        assert llm is not None
        # Mock LLM should respond without API calls
        response = llm.invoke("test prompt")
        assert response is not None
        # LLM returns AIMessage, check content
        assert hasattr(response, 'content')
        assert isinstance(response.content, str)
    
    def test_get_llm_model_returns_string_response(self):
        """LLM should return string responses for testing."""
        from agentic_platform.llm import get_llm_model
        from langchain_core.messages import AIMessage
        llm = get_llm_model(provider="mock")
        result = llm.invoke("What is 2+2?")
        assert isinstance(result, AIMessage)
        assert len(result.content) > 0
    
    def test_list_available_models(self):
        """Should list available models."""
        from agentic_platform.llm import list_available_models
        models = list_available_models()
        assert isinstance(models, dict)
        assert len(models) > 0
        # Should have mock provider
        assert "mock" in models or "MOCK" in str(models)


class TestAgentState:
    """Test AgentState schema."""
    
    def test_agent_state_imports(self):
        """AgentState should be importable."""
        try:
            from agentic_platform.adapters.langgraph_state import AgentState, create_initial_state
            assert AgentState is not None
            assert create_initial_state is not None
        except ImportError as e:
            pytest.fail(f"AgentState import failed: {e}")
    
    def test_create_initial_state(self):
        """Should create valid initial state."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        
        # Verify required fields exist
        assert "messages" in state
        assert "tool_results" in state
        assert "iteration_count" in state
        assert "max_iterations" in state
        assert "should_continue" in state
        assert "memory" in state
        assert "error" in state
        assert "final_status" in state
    
    def test_initial_state_defaults(self):
        """Initial state should have sensible defaults."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state(max_iterations=5)
        
        assert state["iteration_count"] == 0
        assert state["max_iterations"] == 5
        assert state["should_continue"] is True
        assert state["error"] is None
        assert state["final_status"] == "incomplete"
        assert isinstance(state["messages"], list)
        assert isinstance(state["tool_results"], list)


class TestMemoryManager:
    """Test memory management."""
    
    def test_memory_manager_import(self):
        """MemoryManager should be importable."""
        try:
            from agentic_platform.adapters.langgraph_memory import MemoryManager
            assert MemoryManager is not None
        except ImportError as e:
            pytest.fail(f"MemoryManager import failed: {e}")
    
    def test_in_memory_memory_import(self):
        """InMemoryMemory should be importable."""
        try:
            from agentic_platform.adapters.langgraph_memory import InMemoryMemory
            assert InMemoryMemory is not None
        except ImportError as e:
            pytest.fail(f"InMemoryMemory import failed: {e}")
    
    def test_memory_manager_add_entry(self):
        """Should add entries to memory."""
        from agentic_platform.adapters.langgraph_memory import InMemoryMemory
        
        memory = InMemoryMemory()
        memory.add_human("Hello")
        memory.add_assistant("Hi there!")
        
        # Use entries property or get_recent method
        assert len(memory) == 2
        recent = memory.get_recent(2)
        assert len(recent) == 2
        assert recent[0].role == "user"
        assert recent[1].role == "assistant"


class TestToolBinding:
    """Test tool binding for LangChain."""
    
    def test_tool_binding_import(self):
        """ToolBinding should be importable."""
        try:
            from agentic_platform.adapters.langgraph_tools import ToolBinding
            assert ToolBinding is not None
        except ImportError as e:
            pytest.fail(f"ToolBinding import failed: {e}")
    
    def test_tool_registry_import(self):
        """ToolRegistry should be importable."""
        try:
            from agentic_platform.adapters.langgraph_tools import ToolRegistry
            assert ToolRegistry is not None
        except ImportError as e:
            pytest.fail(f"ToolRegistry import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
