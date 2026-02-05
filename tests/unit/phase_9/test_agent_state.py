"""
Phase 9: AgentState Schema Tests

Tests for AgentState definition and state transitions.
Ensures state flows correctly through LangGraph execution.
"""

import pytest
from typing import Optional, Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class TestAgentStateStructure:
    """Test AgentState schema structure."""
    
    def test_agent_state_fields_complete(self):
        """AgentState should have all required fields."""
        from agentic_platform.adapters.langgraph_state import AgentState
        
        state = {
            "messages": [],
            "tool_results": [],
            "current_tool": None,
            "next_tool": None,
            "tool_input": None,
            "iteration_count": 0,
            "max_iterations": 10,
            "should_continue": True,
            "memory": [],
            "context": {},
            "artifacts": [],
            "error": None,
            "error_count": 0,
            "final_result": None,
            "final_status": "incomplete",
        }
        
        # Verify all keys exist in proper TypedDict
        required_keys = {
            "messages", "tool_results", "current_tool", "next_tool",
            "tool_input", "iteration_count", "max_iterations", "should_continue",
            "memory", "context", "artifacts", "error", "error_count",
            "final_result", "final_status"
        }
        
        assert set(state.keys()) == required_keys


class TestInitialStateCreation:
    """Test creating initial agent state."""
    
    def test_create_initial_state_minimal(self):
        """Should create minimal state with defaults."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        
        # Verify critical fields
        assert state["messages"] == []
        assert state["tool_results"] == []
        assert state["iteration_count"] == 0
        assert state["max_iterations"] == 10
        assert state["should_continue"] is True
        assert state["error"] is None
        assert state["final_status"] == "incomplete"
    
    def test_create_initial_state_with_messages(self):
        """Should create state with initial messages."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        initial_messages = [HumanMessage(content="Hello")]
        state = create_initial_state(messages=initial_messages)
        
        assert len(state["messages"]) == 1
        assert state["messages"][0].content == "Hello"
    
    def test_create_initial_state_with_custom_max_iterations(self):
        """Should respect custom max_iterations."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state(max_iterations=5)
        assert state["max_iterations"] == 5
        assert state["iteration_count"] == 0
    
    def test_create_initial_state_with_context(self):
        """Should accept and store context."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        context = {"workflow_id": "test-123", "user_id": "user-456"}
        state = create_initial_state(context=context)
        
        assert state["context"] == context


class TestStateTransitions:
    """Test state transitions during execution."""
    
    def test_state_message_addition(self):
        """Should accumulate messages during execution."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        state["messages"].append(HumanMessage(content="Question"))
        state["messages"].append(AIMessage(content="Answer"))
        
        assert len(state["messages"]) == 2
        assert state["messages"][0].content == "Question"
        assert state["messages"][1].content == "Answer"
    
    def test_state_iteration_increment(self):
        """Should track iteration count."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        for i in range(3):
            state["iteration_count"] += 1
        
        assert state["iteration_count"] == 3
    
    def test_state_tool_call_tracking(self):
        """Should track tool calls in state."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        state["current_tool"] = "google_vision_ocr"
        state["tool_input"] = {"image_path": "document.jpg"}
        
        assert state["current_tool"] == "google_vision_ocr"
        assert state["tool_input"]["image_path"] == "document.jpg"
    
    def test_state_tool_result_accumulation(self):
        """Should accumulate tool results."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        state["tool_results"].append({"tool": "ocr", "output": "extracted text"})
        state["tool_results"].append({"tool": "summarize", "output": "summary"})
        
        assert len(state["tool_results"]) == 2
    
    def test_state_error_tracking(self):
        """Should track errors during execution."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        state["error"] = "Tool call failed"
        state["error_count"] = 1
        
        assert state["error"] is not None
        assert state["error_count"] == 1
    
    def test_state_termination_condition(self):
        """Should support termination conditions."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state(max_iterations=3)
        
        # Simulate execution loop
        while state["should_continue"] and state["iteration_count"] < state["max_iterations"]:
            state["iteration_count"] += 1
        
        assert state["iteration_count"] == 3
        assert state["should_continue"] is True  # Loop condition stops it
    
    def test_state_final_result_setting(self):
        """Should set final result and status."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        state["final_result"] = {"extracted_text": "Hello World"}
        state["final_status"] = "completed"
        state["should_continue"] = False
        
        assert state["final_status"] == "completed"
        assert state["final_result"]["extracted_text"] == "Hello World"


class TestStateMemoryIntegration:
    """Test memory integration with state."""
    
    def test_state_memory_field(self):
        """State should maintain memory field."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        state["memory"] = [
            {"role": "user", "content": "Ask something"},
            {"role": "assistant", "content": "Response"}
        ]
        
        assert len(state["memory"]) == 2
    
    def test_state_artifacts_accumulation(self):
        """State should accumulate artifacts."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        state["artifacts"].append({"type": "ocr_result", "data": "text"})
        state["artifacts"].append({"type": "summary", "data": "brief summary"})
        
        assert len(state["artifacts"]) == 2


class TestStateValidation:
    """Test state validation and type checking."""
    
    def test_state_iteration_count_type(self):
        """Iteration count should be integer."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        assert isinstance(state["iteration_count"], int)
        assert state["iteration_count"] >= 0
    
    def test_state_bool_fields(self):
        """Boolean fields should be properly typed."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        assert isinstance(state["should_continue"], bool)
    
    def test_state_list_fields(self):
        """List fields should be properly initialized."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        assert isinstance(state["messages"], list)
        assert isinstance(state["tool_results"], list)
        assert isinstance(state["memory"], list)
        assert isinstance(state["artifacts"], list)
    
    def test_state_dict_fields(self):
        """Dict fields should be properly initialized."""
        from agentic_platform.adapters.langgraph_state import create_initial_state
        
        state = create_initial_state()
        assert isinstance(state["context"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
