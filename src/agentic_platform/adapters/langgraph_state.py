"""
LangGraph Agent State Schema

Defines the state structure used by LangGraph agents for:
- Message management
- Tool tracking
- Execution context
- Memory management

State flows through the graph and is updated at each node.
"""

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Agent execution state.
    
    This state flows through the LangGraph state machine and is updated
    at each node (agent reasoning, tool execution, etc.).
    
    Attributes:
        messages: Conversation history (all messages including AI, human, tool)
        tool_results: Results from tool executions
        current_tool: Currently executing tool name
        iteration_count: Number of agent iterations so far
        max_iterations: Maximum iterations before stopping
        memory: Long-term memory store for context
        artifacts: Versioned artifacts produced by workflow
    """
    
    # Core messaging
    messages: Annotated[List[BaseMessage], "Chat message history"]
    
    # Tool execution tracking
    tool_results: Annotated[List[Dict[str, Any]], "Results from tool calls"]
    current_tool: Annotated[Optional[str], "Currently executing tool"]
    next_tool: Annotated[Optional[str], "Next tool to call"]
    tool_input: Annotated[Optional[Dict[str, Any]], "Current tool input arguments"]
    
    # Execution control
    iteration_count: Annotated[int, "Number of iterations completed"]
    max_iterations: Annotated[int, "Maximum iterations before stopping (default: 10)"]
    should_continue: Annotated[bool, "Whether agent should continue iterating"]
    
    # Memory and context
    memory: Annotated[List[Dict[str, str]], "Conversation memory for context"]
    context: Annotated[Dict[str, Any], "Additional execution context"]
    
    # Workflow artifacts
    artifacts: Annotated[List[Dict[str, Any]], "Versioned artifacts from workflow"]
    
    # Error handling
    error: Annotated[Optional[str], "Error message if one occurred"]
    error_count: Annotated[int, "Number of errors encountered"]
    
    # Final result
    final_result: Annotated[Optional[Dict[str, Any]], "Final workflow result"]
    final_status: Annotated[str, "Final status: 'completed', 'failed', or 'incomplete'"]


def create_initial_state(
    messages: Optional[List[BaseMessage]] = None,
    max_iterations: int = 10,
    context: Optional[Dict[str, Any]] = None,
) -> AgentState:
    """
    Create initial agent state.
    
    Args:
        messages: Initial messages (if any)
        max_iterations: Maximum iterations for agent
        context: Additional context data
    
    Returns:
        Initial AgentState ready for execution
    """
    from langchain_core.messages import HumanMessage
    
    return {
        "messages": messages or [],
        "tool_results": [],
        "current_tool": None,
        "next_tool": None,
        "tool_input": None,
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "should_continue": True,
        "memory": [],
        "context": context or {},
        "artifacts": [],
        "error": None,
        "error_count": 0,
        "final_result": None,
        "final_status": "incomplete",
    }


class ToolResultMessage(TypedDict):
    """Tool execution result."""
    tool_name: str
    tool_input: Dict[str, Any]
    result: Any
    timestamp: str


class MemoryEntry(TypedDict):
    """Memory entry for conversation context."""
    role: str  # "user", "assistant", "tool"
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]]


class ArtifactMetadata(TypedDict):
    """Artifact metadata for versioning."""
    artifact_id: str
    version: int
    created_at: str
    source_node: str
    checksum: str
    artifact_type: str  # "ocr_result", "analysis", "summary", etc.
