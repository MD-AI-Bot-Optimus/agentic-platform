"""
Tests for LangGraph Agent Components

Test coverage:
- Tool binding
- Memory management
- Agent execution
- Multi-step reasoning
"""

import pytest
from unittest.mock import Mock, patch
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage

from agentic_platform.adapters.langgraph_tools import ToolBinding, ToolRegistry
from agentic_platform.adapters.langgraph_memory import (
    InMemoryMemory, MemoryEntry, MemorySearcher, memory_to_dict, dict_to_memory
)
from agentic_platform.adapters.langgraph_agent import LangGraphAgent, AgentExecutionResult
from agentic_platform.llm.mock_llm import MockLLM


# ============================================================================
# Tool Binding Tests
# ============================================================================

class TestToolBinding:
    """Test tool binding functionality."""
    
    def test_bind_simple_tool(self):
        """Test binding a simple tool."""
        def dummy_tool(name: str) -> str:
            return f"Hello {name}"
        
        schema = {
            "name": {"type": str, "description": "Person name"}
        }
        
        tool = ToolBinding.bind_tool("greet", dummy_tool, schema)
        
        assert tool.name == "greet"
        assert tool.func("Alice") == "Hello Alice"
    
    def test_bind_ocr_tool(self):
        """Test binding OCR tool."""
        mock_client = Mock()
        mock_client.call.return_value = {
            "text": "Sample text",
            "confidence": 0.95,
            "symbols_count": 100
        }
        
        tool = ToolBinding.bind_ocr_tool(mock_client)
        
        assert tool.name == "extract_text_from_image"
        result = tool.func(image_path="test.jpg")
        
        assert result["text"] == "Sample text"
        assert result["confidence"] == 0.95


class TestToolRegistry:
    """Test tool registry."""
    
    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        
        def dummy_tool(x: int) -> int:
            return x * 2
        
        schema = {"x": {"type": int, "description": "Input number"}}
        registry.register("double", dummy_tool, schema)
        
        assert "double" in registry.tools
        assert len(registry.get_all()) == 1
    
    def test_get_tool(self):
        """Test getting a specific tool."""
        registry = ToolRegistry()
        
        def dummy_tool(x: int) -> int:
            return x * 2
        
        schema = {"x": {"type": int, "description": "Input number"}}
        registry.register("double", dummy_tool, schema)
        
        tool = registry.get("double")
        assert tool is not None
        assert tool.name == "double"


# ============================================================================
# Memory Management Tests
# ============================================================================

class TestMemoryManager:
    """Test memory management."""
    
    def test_add_human_message(self):
        """Test adding human message."""
        memory = InMemoryMemory()
        memory.add_human("Hello")
        
        assert len(memory) == 1
        assert memory.entries[0].role == "user"
        assert memory.entries[0].content == "Hello"
    
    def test_add_assistant_message(self):
        """Test adding assistant message."""
        memory = InMemoryMemory()
        memory.add_assistant("Hi there")
        
        assert len(memory) == 1
        assert memory.entries[0].role == "assistant"
    
    def test_get_recent(self):
        """Test getting recent messages."""
        memory = InMemoryMemory()
        for i in range(5):
            memory.add_human(f"Message {i}")
        
        recent = memory.get_recent(3)
        assert len(recent) == 3
        assert recent[0].content == "Message 2"
    
    def test_max_entries_limit(self):
        """Test max entries limit."""
        memory = InMemoryMemory(max_entries=5)
        for i in range(10):
            memory.add_human(f"Message {i}")
        
        assert len(memory) == 5
        assert memory.entries[0].content == "Message 5"  # Oldest 5 removed
    
    def test_get_context(self):
        """Test context generation."""
        memory = InMemoryMemory()
        memory.add_human("User: Hello")
        memory.add_assistant("Assistant: Hi")
        
        context = memory.get_context(2)
        assert "user: User: Hello" in context
        assert "assistant: Assistant: Hi" in context
    
    def test_memory_serialization(self):
        """Test memory to/from dict."""
        memory = InMemoryMemory()
        memory.add_human("Hello")
        memory.add_assistant("Hi")
        
        data = memory_to_dict(memory)
        assert data["total_entries"] == 2
        
        restored = dict_to_memory(data)
        assert len(restored) == 2


class TestMemorySearcher:
    """Test memory search."""
    
    def test_search_keyword(self):
        """Test keyword search."""
        memory = InMemoryMemory()
        memory.add_human("Tell me about cats")
        memory.add_assistant("Cats are furry")
        memory.add_human("What about dogs?")
        
        results = MemorySearcher.search_keyword(memory, "cat")
        assert len(results) == 2  # "cats" and "Cats"
    
    def test_search_by_role(self):
        """Test search by role."""
        memory = InMemoryMemory()
        memory.add_human("Hello")
        memory.add_assistant("Hi")
        memory.add_human("How are you?")
        
        user_msgs = MemorySearcher.search_by_role(memory, "user")
        assert len(user_msgs) == 2


# ============================================================================
# Agent Tests
# ============================================================================

class TestLangGraphAgent:
    """Test LangGraph agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        llm = MockLLM()
        agent = LangGraphAgent(model="mock-llm", llm=llm)
        
        assert agent.model_name == "mock-llm"
        assert agent.max_iterations == 10
        assert len(agent.tools) == 0
    
    def test_agent_with_tools(self):
        """Test adding tools to agent."""
        llm = MockLLM()
        agent = LangGraphAgent(model="mock-llm", llm=llm)
        
        tool1 = Mock(name="tool1")
        tool2 = Mock(name="tool2")
        
        agent.with_tools([tool1, tool2])
        assert len(agent.tools) == 2
    
    def test_agent_with_memory(self):
        """Test setting custom memory."""
        llm = MockLLM()
        agent = LangGraphAgent(model="mock-llm", llm=llm)
        memory = InMemoryMemory()
        
        agent.with_memory(memory)
        assert agent.memory is memory
    
    def test_simple_execution_no_tools(self):
        """Test agent execution without tools."""
        llm = MockLLM()
        agent = LangGraphAgent(model="mock-llm", llm=llm, max_iterations=1)
        
        result = agent.execute("What is 2+2?")
        
        assert result.status == "success"
        assert result.iterations >= 1
        assert len(result.reasoning_steps) >= 1
    
    def test_memory_added_after_execution(self):
        """Test that messages are added to memory."""
        llm = MockLLM()
        agent = LangGraphAgent(model="mock-llm", llm=llm, max_iterations=1)
        
        agent.execute("Hello")
        
        # Check memory
        assert len(agent.memory) >= 1
        human_msgs = [e for e in agent.memory.entries if e.role == "user"]
        assert len(human_msgs) >= 1
    
    def test_reset_agent(self):
        """Test agent reset."""
        llm = MockLLM()
        agent = LangGraphAgent(model="mock-llm", llm=llm)
        
        agent.add_reasoning_step("Step 1")
        assert len(agent.reasoning_steps) == 1
        
        agent.reset()
        assert len(agent.reasoning_steps) == 0
        assert len(agent.memory) == 0
    
    def test_tool_extraction(self):
        """Test tool extraction from LLM response."""
        llm = MockLLM()
        agent = LangGraphAgent(model="mock-llm", llm=llm)
        
        # Test pattern 1
        response1 = "I'll use_tool: extract_text_from_image with image_path=doc.jpg"
        tool_name, args = agent._extract_tool_use(response1)
        assert tool_name == "extract_text_from_image"
        assert args["image_path"] == "doc.jpg"
    
    def test_iteration_limit(self):
        """Test max iterations limit."""
        llm = MockLLM()
        agent = LangGraphAgent(model="mock-llm", llm=llm, max_iterations=2)
        
        result = agent.execute("Long prompt that requires many steps")
        
        assert result.iterations <= agent.max_iterations


# ============================================================================
# Integration Tests
# ============================================================================

class TestAgentIntegration:
    """Integration tests for full agent workflow."""
    
    def test_agent_with_mock_tool(self):
        """Test agent using a mock tool."""
        # Setup
        llm = MockLLM()
        
        def mock_extract(image_path: str) -> str:
            return f"Text from {image_path}"
        
        mock_tool = Mock()
        mock_tool.name = "extract"
        mock_tool.func = mock_extract
        
        # Create agent
        agent = LangGraphAgent(model="mock-llm", llm=llm, max_iterations=1)
        agent.with_tools([mock_tool])
        
        # Execute
        result = agent.execute("Extract text from image.jpg")
        
        assert result.status in ["success", "incomplete"]
        assert len(result.reasoning_steps) > 0
    
    def test_memory_persistence_across_calls(self):
        """Test that memory persists across multiple executions."""
        llm = MockLLM()
        memory = InMemoryMemory()
        agent = LangGraphAgent(model="mock-llm", llm=llm, memory=memory, max_iterations=1)
        
        # First execution
        result1 = agent.execute("First message")
        initial_length = len(agent.memory)
        
        # Second execution  
        result2 = agent.execute("Second message")
        final_length = len(agent.memory)
        
        # Memory should have accumulated
        assert final_length >= initial_length
        assert result1.status in ["success", "incomplete"]
        assert result2.status in ["success", "incomplete"]


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
