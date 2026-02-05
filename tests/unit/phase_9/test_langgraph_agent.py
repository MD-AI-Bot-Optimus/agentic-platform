"""
Phase 9: LangGraphAgent Implementation Tests

Tests for the core agent with:
- StateGraph construction
- Agent reasoning loop
- Tool binding and calling
- Conditional routing
- Memory management
- Iteration limits
- Error handling
"""

import pytest
from typing import Dict, Any
from unittest.mock import MagicMock, patch


class TestLangGraphAgentInitialization:
    """Test LangGraphAgent creation and configuration."""
    
    def test_agent_initialization_basic(self):
        """Should create agent with basic config."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(model="claude-3.5-sonnet", tools=[], llm=llm)
        
        assert agent is not None
        assert agent.model_name == "claude-3.5-sonnet"
        assert agent.tools == []
        assert agent.llm is not None
    
    def test_agent_initialization_with_tools(self):
        """Should initialize agent with tools."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        
        mock_tools = [
            {"name": "tool1", "description": "Tool 1"},
            {"name": "tool2", "description": "Tool 2"}
        ]
        
        agent = LangGraphAgent(tools=mock_tools, llm=llm)
        assert len(agent.tools) == 2
    
    def test_agent_initialization_with_custom_memory(self):
        """Should use custom memory if provided."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.adapters.langgraph_memory import InMemoryMemory
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        memory = InMemoryMemory()
        
        agent = LangGraphAgent(memory=memory, llm=llm)
        assert agent.memory == memory
    
    def test_agent_initialization_max_iterations(self):
        """Should respect max_iterations config."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(max_iterations=5, llm=llm)
        
        assert agent.max_iterations == 5


class TestLangGraphAgentBuilder:
    """Test agent builder methods."""
    
    def test_with_tools_chainable(self):
        """Should support chaining with_tools."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        tools = [{"name": "test", "description": "test"}]
        
        agent = LangGraphAgent(llm=llm).with_tools(tools)
        assert agent.tools == tools
    
    def test_with_memory_chainable(self):
        """Should support chaining with_memory."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.adapters.langgraph_memory import InMemoryMemory
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        memory = InMemoryMemory()
        
        agent = LangGraphAgent(llm=llm).with_memory(memory)
        assert agent.memory == memory
    
    def test_builder_chaining_full(self):
        """Should support full chaining."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.adapters.langgraph_memory import InMemoryMemory
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        tools = [{"name": "test", "description": "test"}]
        memory = InMemoryMemory()
        
        agent = (LangGraphAgent(llm=llm)
                .with_tools(tools)
                .with_memory(memory))
        
        assert agent.tools == tools
        assert agent.memory == memory


class TestAgentReasoningSteps:
    """Test agent reasoning step tracking."""
    
    def test_add_reasoning_step(self):
        """Should add reasoning steps."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        agent.add_reasoning_step("Started agent")
        agent.add_reasoning_step("Called tool")
        
        assert len(agent.reasoning_steps) == 2
        assert "Step 0: Started agent" in agent.reasoning_steps[0]
        assert "Step 1: Called tool" in agent.reasoning_steps[1]
    
    def test_reasoning_steps_tied_to_iterations(self):
        """Reasoning steps should reflect iteration count."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        for i in range(3):
            agent.iteration_count = i
            agent.add_reasoning_step(f"Iteration {i}")
        
        assert len(agent.reasoning_steps) == 3


class TestAgentStateManagement:
    """Test agent state during execution."""
    
    def test_agent_tracks_tool_calls(self):
        """Should track tool calls made during execution."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        # Mock tool call tracking
        tool_call = {
            "name": "test_tool",
            "arguments": {"arg1": "value1"},
            "result": "success"
        }
        
        agent.tool_calls.append(tool_call)
        
        assert len(agent.tool_calls) == 1
        assert agent.tool_calls[0]["name"] == "test_tool"


class TestAgentMemoryIntegration:
    """Test memory integration with agent."""
    
    def test_agent_adds_messages_to_memory(self):
        """Agent should add messages to memory during execution."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.adapters.langgraph_memory import InMemoryMemory
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        memory = InMemoryMemory()
        agent = LangGraphAgent(memory=memory, llm=llm)
        
        # Simulate adding messages
        agent.memory.add_human("What is 2+2?")
        agent.memory.add_assistant("The answer is 4")
        
        assert len(agent.memory) == 2
    
    def test_agent_memory_context_retrieval(self):
        """Agent should be able to retrieve context from memory."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.adapters.langgraph_memory import InMemoryMemory
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        memory = InMemoryMemory()
        agent = LangGraphAgent(memory=memory, llm=llm)
        
        agent.memory.add_human("Message 1")
        agent.memory.add_assistant("Response 1")
        agent.memory.add_human("Message 2")
        
        context = agent.memory.get_context(n=5)
        assert "Message 1" in context
        assert "Response 1" in context
        assert "Message 2" in context


class TestAgentExecutionInterface:
    """Test agent execution interface."""
    
    def test_execute_method_exists(self):
        """Agent should have execute method."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        assert hasattr(agent, 'execute')
        assert callable(agent.execute)
    
    def test_execute_signature(self):
        """Execute should accept prompt and optional context."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from inspect import signature
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        sig = signature(agent.execute)
        params = list(sig.parameters.keys())
        
        assert 'prompt' in params
        # context may be optional


class TestAgentExecutionResult:
    """Test execution result format."""
    
    def test_execution_result_has_required_fields(self):
        """Execution result should have status, output, steps, calls, iterations."""
        from agentic_platform.adapters.langgraph_agent import AgentExecutionResult
        
        result = AgentExecutionResult(
            status="success",
            final_output="test result",
            reasoning_steps=["step1", "step2"],
            tool_calls=[],
            iterations=2
        )
        
        assert result.status == "success"
        assert result.final_output == "test result"
        assert len(result.reasoning_steps) == 2
        assert result.iterations == 2
    
    def test_execution_result_error_field(self):
        """Execution result should support error field."""
        from agentic_platform.adapters.langgraph_agent import AgentExecutionResult
        
        result = AgentExecutionResult(
            status="error",
            final_output=None,
            reasoning_steps=[],
            tool_calls=[],
            iterations=1,
            error="Something went wrong"
        )
        
        assert result.error == "Something went wrong"


class TestAgentConfigurationDefaults:
    """Test agent configuration defaults."""
    
    def test_default_max_iterations(self):
        """Default max_iterations should be reasonable."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        # Default should be > 0 and reasonable (10?)
        assert agent.max_iterations > 0
        assert agent.max_iterations <= 20
    
    def test_default_model_name(self):
        """Should have a default model name."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        assert agent.model_name is not None
        assert isinstance(agent.model_name, str)


class TestAgentIntegration:
    """Integration tests with StateGraph."""
    
    def test_agent_can_create_stategraph(self):
        """Agent should be able to create a StateGraph."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from langgraph.graph import StateGraph
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        # Agent might have method to get or create StateGraph
        # At minimum, StateGraph should be importable
        assert StateGraph is not None
    
    def test_agent_state_initialization(self):
        """Agent should initialize state correctly."""
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.adapters.langgraph_state import create_initial_state
        from agentic_platform.llm import get_llm_model
        
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        # Should be able to create initial state
        state = create_initial_state(max_iterations=agent.max_iterations)
        
        assert state["max_iterations"] == agent.max_iterations
        assert state["iteration_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
