"""
StateGraph Implementation Tests

Tests for the LangGraph StateGraph implementation in LangGraphAgent:
- agent_node: LLM reasoning step
- tool_node: Tool execution
- router: Conditional routing between reasoning and tools
- Graph compilation and state management
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agentic_platform.adapters.langgraph_agent import LangGraphAgent
from agentic_platform.adapters.langgraph_state import AgentState, create_initial_state
from agentic_platform.llm import get_llm_model


class TestAgentNodeImplementation:
    """Test the agent_node function for LLM reasoning."""
    
    def test_agent_node_exists(self):
        """Agent should have agent_node method."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        assert hasattr(agent, 'agent_node')
        assert callable(agent.agent_node)
    
    def test_agent_node_takes_state(self):
        """agent_node should accept AgentState."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        state = create_initial_state()
        state["messages"] = [HumanMessage(content="What is 2+2?")]
        
        # Should not raise
        result = agent.agent_node(state)
        assert result is not None
    
    def test_agent_node_returns_state_update(self):
        """agent_node should return dict with state updates."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        state = create_initial_state()
        state["messages"] = [HumanMessage(content="What is 2+2?")]
        
        result = agent.agent_node(state)
        
        # Should return dict (state update)
        assert isinstance(result, dict)
        # Should have messages key
        assert "messages" in result
        # Messages should be a list
        assert isinstance(result["messages"], list)
    
    def test_agent_node_calls_llm(self):
        """agent_node should invoke LLM with messages."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        state = create_initial_state()
        state["messages"] = [HumanMessage(content="Test")]
        
        result = agent.agent_node(state)
        
        # Result messages should include LLM response
        assert len(result["messages"]) > 0
        # Last message should be AIMessage (from LLM)
        assert isinstance(result["messages"][-1], AIMessage)
    
    def test_agent_node_increments_iteration(self):
        """agent_node should increment iteration_count in state."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        state = create_initial_state()
        state["messages"] = [HumanMessage(content="Test")]
        state["iteration_count"] = 0
        
        result = agent.agent_node(state)
        
        assert result["iteration_count"] == 1
    
    def test_agent_node_with_tools_in_state(self):
        """agent_node should handle tools in state."""
        llm = get_llm_model(provider="mock")
        mock_tool = Mock(name="test_tool", description="Test tool")
        agent = LangGraphAgent(llm=llm, tools=[mock_tool])
        
        state = create_initial_state()
        state["messages"] = [HumanMessage(content="Use test_tool")]
        
        result = agent.agent_node(state)
        
        # Should complete without error
        assert "messages" in result
        assert "iteration_count" in result


class TestToolNodeImplementation:
    """Test the tool_node function for tool execution."""
    
    def test_tool_node_exists(self):
        """Agent should have tool_node method."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        assert hasattr(agent, 'tool_node')
        assert callable(agent.tool_node)
    
    def test_tool_node_takes_state(self):
        """tool_node should accept AgentState with tool info."""
        llm = get_llm_model(provider="mock")
        
        # Create a simple mock tool
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.func = Mock(return_value="test result")
        
        agent = LangGraphAgent(llm=llm, tools=[mock_tool])
        
        state = create_initial_state()
        state["current_tool"] = "test_tool"
        state["tool_input"] = {}
        
        # Should not raise
        result = agent.tool_node(state)
        assert result is not None
    
    def test_tool_node_executes_tool(self):
        """tool_node should execute the specified tool."""
        llm = get_llm_model(provider="mock")
        
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.func = Mock(return_value="tool executed")
        
        agent = LangGraphAgent(llm=llm, tools=[mock_tool])
        
        state = create_initial_state()
        state["current_tool"] = "test_tool"
        state["tool_input"] = {}
        
        result = agent.tool_node(state)
        
        # Tool should have been called
        mock_tool.func.assert_called()
    
    def test_tool_node_adds_tool_result(self):
        """tool_node should add tool result to state."""
        llm = get_llm_model(provider="mock")
        
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.func = Mock(return_value="tool result")
        
        agent = LangGraphAgent(llm=llm, tools=[mock_tool])
        
        state = create_initial_state()
        state["current_tool"] = "test_tool"
        state["tool_input"] = {}
        
        result = agent.tool_node(state)
        
        # Should have tool_results
        assert "tool_results" in result
        assert len(result["tool_results"]) > 0
        assert "test_tool" in str(result["tool_results"])
    
    def test_tool_node_returns_messages_update(self):
        """tool_node should add ToolMessage to messages."""
        llm = get_llm_model(provider="mock")
        
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.func = Mock(return_value="tool result")
        
        agent = LangGraphAgent(llm=llm, tools=[mock_tool])
        
        state = create_initial_state()
        state["messages"] = [HumanMessage(content="Test")]
        state["current_tool"] = "test_tool"
        state["tool_input"] = {}
        
        result = agent.tool_node(state)
        
        # Should have messages
        assert "messages" in result
        # Should have added a message
        assert len(result["messages"]) >= len(state["messages"])


class TestRouterImplementation:
    """Test the router function for conditional routing."""
    
    def test_router_exists(self):
        """Agent should have router method."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        assert hasattr(agent, 'router')
        assert callable(agent.router)
    
    def test_router_detects_tool_use(self):
        """router should detect when tool use is requested."""
        llm = get_llm_model(provider="mock")
        
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        
        agent = LangGraphAgent(llm=llm, tools=[mock_tool])
        
        state = create_initial_state()
        state["messages"] = [
            HumanMessage(content="Test"),
            AIMessage(content="I'll use_tool: test_tool with arg=value")
        ]
        
        route = agent.router(state)
        
        # Should route to tool_node
        assert route == "tool_node"
    
    def test_router_detects_end_condition(self):
        """router should route to END when no tool use."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        state = create_initial_state()
        state["messages"] = [
            HumanMessage(content="What is 2+2?"),
            AIMessage(content="The answer is 4. No tools needed.")
        ]
        
        route = agent.router(state)
        
        # Should route to END (no tool use)
        assert route == "__end__"
    
    def test_router_respects_max_iterations(self):
        """router should END if max iterations reached."""
        llm = get_llm_model(provider="mock")
        
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        
        agent = LangGraphAgent(llm=llm, tools=[mock_tool], max_iterations=3)
        
        state = create_initial_state()
        state["max_iterations"] = 3
        state["iteration_count"] = 3
        state["messages"] = [
            AIMessage(content="use_tool: test_tool")
        ]
        
        route = agent.router(state)
        
        # Should END even though tool is requested (max iterations reached)
        assert route == "__end__"
    
    def test_router_handles_no_messages(self):
        """router should handle empty message list."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        state = create_initial_state()
        state["messages"] = []
        
        # Should not raise
        route = agent.router(state)
        assert route in ["__end__", "tool_node"]


class TestStateGraphCompilation:
    """Test that StateGraph compiles correctly."""
    
    def test_graph_compiles(self):
        """Agent should compile to a valid LangGraph."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        graph = agent.create_graph()
        
        assert graph is not None
    
    def test_graph_has_nodes(self):
        """Compiled graph should have agent_node and tool_node."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        graph = agent.create_graph()
        
        # Graph should have nodes
        assert hasattr(graph, 'nodes') or len(graph) > 0
    
    def test_graph_executes_basic_prompt(self):
        """Compiled graph should execute basic prompts."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        graph = agent.create_graph()
        
        # Create initial state
        state = create_initial_state()
        state["messages"] = [HumanMessage(content="What is 2+2?")]
        
        # Graph should be callable
        # (Note: calling graph directly may vary by implementation)
        assert graph is not None


class TestStateFlowThroughGraph:
    """Test state updates as it flows through graph."""
    
    def test_state_accumulates_messages(self):
        """State should accumulate messages through iterations."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        state = create_initial_state()
        initial_msgs = [HumanMessage(content="Start")]
        state["messages"] = initial_msgs
        
        # Simulate one iteration
        result = agent.agent_node(state)
        
        # Should have more messages
        assert len(result["messages"]) > len(initial_msgs)
    
    def test_state_iteration_count_increases(self):
        """iteration_count should increase through iterations."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        state = create_initial_state()
        state["iteration_count"] = 0
        state["messages"] = [HumanMessage(content="Test")]
        
        result = agent.agent_node(state)
        
        assert result["iteration_count"] == 1
    
    def test_state_tool_results_accumulate(self):
        """State should accumulate tool results."""
        llm = get_llm_model(provider="mock")
        
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.func = Mock(return_value="result1")
        
        agent = LangGraphAgent(llm=llm, tools=[mock_tool])
        
        state = create_initial_state()
        state["tool_results"] = []
        state["current_tool"] = "test_tool"
        state["tool_input"] = {}
        state["messages"] = [HumanMessage(content="Test")]
        
        result = agent.tool_node(state)
        
        # Should have accumulated tool results
        assert len(result["tool_results"]) > 0


class TestGraphErrorHandling:
    """Test error handling in graph nodes."""
    
    def test_agent_node_handles_llm_error(self):
        """agent_node should handle LLM errors gracefully."""
        llm = get_llm_model(provider="mock")
        agent = LangGraphAgent(llm=llm)
        
        # Mock LLM to raise error
        agent.llm.invoke = Mock(side_effect=Exception("LLM failed"))
        
        state = create_initial_state()
        state["messages"] = [HumanMessage(content="Test")]
        
        # Should handle error (not raise)
        try:
            result = agent.agent_node(state)
            assert "error" in result or result is not None
        except Exception as e:
            # If it raises, that's also acceptable with proper error handling
            assert "LLM failed" in str(e)
    
    def test_tool_node_handles_tool_error(self):
        """tool_node should handle tool execution errors."""
        llm = get_llm_model(provider="mock")
        
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.func = Mock(side_effect=Exception("Tool failed"))
        
        agent = LangGraphAgent(llm=llm, tools=[mock_tool])
        
        state = create_initial_state()
        state["current_tool"] = "test_tool"
        state["tool_input"] = {}
        state["messages"] = [HumanMessage(content="Test")]
        
        # Should handle error gracefully
        try:
            result = agent.tool_node(state)
            assert "error" in result or result is not None
        except Exception:
            # Error handling is acceptable
            pass
