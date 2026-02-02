"""
LangGraph Agent - Core Agent Implementation

Implements a reasoning agent that:
- Uses LLM to decide which tools to use
- Executes tools autonomously
- Maintains conversation memory
- Handles multi-step reasoning
- Iterates until completion or max iterations

Usage:
    agent = LangGraphAgent(model="claude-3.5-sonnet", tools=[ocr_tool])
    result = agent.execute("Extract text from document.jpg")
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from agentic_platform.adapters.langgraph_state import AgentState, create_initial_state
from agentic_platform.adapters.langgraph_memory import MemoryManager, InMemoryMemory
from agentic_platform.adapters.langgraph_tools import ToolBinding, ToolRegistry
from agentic_platform.llm import get_llm_model

logger = logging.getLogger(__name__)


@dataclass
class AgentExecutionResult:
    """Result from agent execution."""
    status: str  # "success", "incomplete", "error"
    final_output: Any
    reasoning_steps: List[str]
    tool_calls: List[Dict[str, Any]]
    iterations: int
    error: Optional[str] = None


class LangGraphAgent:
    """
    Reasoning agent that uses LLM to orchestrate tool use.
    
    Process:
    1. User provides prompt
    2. Agent (LLM) reasons about what to do
    3. If tool needed, agent decides which tool and arguments
    4. Tool executes
    5. Agent gets result and decides next step
    6. Repeat until done or max iterations reached
    """
    
    def __init__(
        self,
        model: str = "claude-3.5-sonnet",
        tools: Optional[List] = None,
        max_iterations: int = 10,
        memory: Optional[MemoryManager] = None,
        llm: Optional[LLM] = None,
    ):
        """
        Initialize agent.
        
        Args:
            model: Model name (e.g., "claude-3.5-sonnet", "gpt-4-turbo")
            tools: List of LangChain StructuredTools
            max_iterations: Max reasoning iterations
            memory: Memory manager for conversation history
            llm: LLM instance (if None, creates one from model name)
        """
        self.model_name = model
        self.max_iterations = max_iterations
        self.tools = tools or []
        self.memory = memory or InMemoryMemory()
        self.llm = llm or get_llm_model(model=model)
        
        # State tracking
        self.iteration_count = 0
        self.reasoning_steps: List[str] = []
        self.tool_calls: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized LangGraphAgent (model={model}, tools={len(self.tools)}, max_iter={max_iterations})")
    
    def with_tools(self, tools: List) -> "LangGraphAgent":
        """Add tools to agent."""
        self.tools = tools
        logger.info(f"Added {len(tools)} tools to agent")
        return self
    
    def with_memory(self, memory: MemoryManager) -> "LangGraphAgent":
        """Set memory manager."""
        self.memory = memory
        logger.info(f"Set memory manager: {memory}")
        return self
    
    def add_reasoning_step(self, step: str) -> None:
        """Record a reasoning step."""
        self.reasoning_steps.append(f"Step {self.iteration_count}: {step}")
    
    def execute(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> AgentExecutionResult:
        """
        Execute agent on prompt.
        
        Args:
            prompt: User prompt
            context: Additional context
        
        Returns:
            AgentExecutionResult with output and reasoning
        """
        self.iteration_count = 0
        self.reasoning_steps = []
        self.tool_calls = []
        
        logger.info(f"Starting agent execution: {prompt[:50]}...")
        
        # Add to memory
        self.memory.add_human(prompt)
        
        # Initialize state
        messages = [HumanMessage(content=prompt)]
        
        try:
            # Main loop
            for iteration in range(self.max_iterations):
                self.iteration_count = iteration + 1
                
                logger.debug(f"Iteration {self.iteration_count}/{self.max_iterations}")
                
                # Get LLM response
                response = self._get_llm_response(messages)
                
                if not response:
                    logger.warning("No LLM response")
                    break
                
                response_text = response.content if hasattr(response, 'content') else str(response)
                self.add_reasoning_step(f"LLM: {response_text[:100]}")
                
                # Add to messages
                messages.append(AIMessage(content=response_text))
                self.memory.add_assistant(response_text)
                
                # Check if tool use is needed
                tool_name, tool_args = self._extract_tool_use(response_text)
                
                if tool_name:
                    # Execute tool
                    logger.info(f"Executing tool: {tool_name}")
                    self.add_reasoning_step(f"Tool: {tool_name}({tool_args})")
                    
                    result = self._execute_tool(tool_name, tool_args)
                    self.tool_calls.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result
                    })
                    self.memory.add_tool_result(tool_name, result)
                    
                    # Add tool result to conversation
                    tool_msg = f"Tool {tool_name} result: {result}"
                    messages.append(HumanMessage(content=tool_msg))
                    self.add_reasoning_step(f"Tool result: {str(result)[:100]}")
                
                else:
                    # No tool needed - agent has final answer
                    logger.info(f"Agent reached conclusion after {self.iteration_count} iterations")
                    return AgentExecutionResult(
                        status="success",
                        final_output=response_text,
                        reasoning_steps=self.reasoning_steps,
                        tool_calls=self.tool_calls,
                        iterations=self.iteration_count
                    )
            
            # Max iterations reached
            logger.warning(f"Max iterations ({self.max_iterations}) reached")
            return AgentExecutionResult(
                status="incomplete",
                final_output=messages[-1].content if messages else None,
                reasoning_steps=self.reasoning_steps,
                tool_calls=self.tool_calls,
                iterations=self.iteration_count,
                error=f"Max iterations ({self.max_iterations}) reached"
            )
        
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return AgentExecutionResult(
                status="error",
                final_output=None,
                reasoning_steps=self.reasoning_steps,
                tool_calls=self.tool_calls,
                iterations=self.iteration_count,
                error=str(e)
            )
    
    def _get_llm_response(self, messages: List[BaseMessage]) -> Optional[Any]:
        """Get response from LLM."""
        try:
            response = self.llm.invoke(messages)
            return response
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None
    
    def _extract_tool_use(self, response_text: str) -> tuple[Optional[str], Optional[Dict]]:
        """
        Extract tool use from LLM response.
        
        Looks for patterns like:
        - "use_tool: extract_text_from_image with image_path=document.jpg"
        - "{\"tool\": \"extract_text_from_image\", \"args\": {...}}"
        """
        import re
        import json
        
        # Pattern 1: use_tool: name with args
        match = re.search(r"use_tool:\s*(\w+)\s*(?:with\s+(.+))?", response_text, re.IGNORECASE)
        if match:
            tool_name = match.group(1)
            args_str = match.group(2)
            args = {}
            if args_str:
                # Parse arguments
                arg_pairs = re.findall(r"(\w+)=([^,\s]+)", args_str)
                args = {k: v.strip("'\"") for k, v in arg_pairs}
            return tool_name, args
        
        # Pattern 2: JSON tool use
        match = re.search(r'\{.*?"tool":\s*"(\w+)".*?"args":\s*({.*?})', response_text)
        if match:
            tool_name = match.group(1)
            try:
                args = json.loads(match.group(2))
                return tool_name, args
            except json.JSONDecodeError:
                pass
        
        return None, None
    
    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """Execute a tool."""
        # Find tool
        tool = None
        for t in self.tools:
            if t.name == tool_name or t.name.replace("_", " ") == tool_name:
                tool = t
                break
        
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Execute
        try:
            result = tool.func(**tool_args) if tool_args else tool.func()
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise
    
    def reset(self) -> None:
        """Reset agent state."""
        self.iteration_count = 0
        self.reasoning_steps = []
        self.tool_calls = []
        self.memory.clear()
        logger.info("Agent reset")
    
    def get_memory_context(self) -> str:
        """Get formatted memory context."""
        return self.memory.get_context(10)
