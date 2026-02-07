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
import re
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END

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
        llm: Optional[Any] = None,
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
        # Use provided memory or create new one
        if memory is not None:
            self.memory = memory
        else:
            self.memory = InMemoryMemory()
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
        step_num = len(self.reasoning_steps)
        self.reasoning_steps.append(f"Step {step_num}: {step}")
    
    def agent_node(self, state: AgentState) -> Dict[str, Any]:
        """
        LLM reasoning node.
        
        Calls LLM with current messages and returns updated state.
        This is the main reasoning step where the agent decides what to do.
        
        Args:
            state: Current agent state
        
        Returns:
            State update with new messages and incremented iteration count
        """
        messages = state["messages"]
        iteration = state["iteration_count"] + 1
        
        logger.debug(f"Agent node: iteration {iteration}")
        
        try:
            # Get LLM response
            response = self.llm.invoke(messages)
            
            if response is None:
                logger.warning("LLM returned None")
                return {
                    "messages": messages,
                    "iteration_count": iteration,
                    "error": "LLM returned no response"
                }
            
            # Extract response content
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            logger.debug(f"LLM response: {response_text[:100]}")
            
            # Add response as AIMessage
            new_messages = messages + [AIMessage(content=response_text)]
            
            # Detect Persona Switch
            persona = self._extract_persona(response_text)
            if persona:
                self.add_reasoning_step(f"**Persona Switch**: 🔄 Handing off to *{persona}*")
                # Add a specific event for UI to render a handoff node
                self.tool_calls.append({
                    "tool": "persona_handoff",
                    "args": {"to": persona},
                    "result": f"Switched to {persona}"
                })
            
            # Track reasoning step
            # Clean up the response text for the step log (optional, but keeps it clean)
            clean_text = response_text.replace(f"[{persona}]:", "").strip() if persona else response_text
            self.add_reasoning_step(f"LLM: {clean_text[:150]}..." if len(clean_text) > 150 else f"LLM: {clean_text}")
            
            # Add to memory
            self.memory.add_assistant(response_text)
            
            # Check for tool use immediately and update state
            tool_name, tool_args = self._extract_tool_use(response_text)
            
            result = {
                "messages": new_messages,
                "iteration_count": iteration,
            }
            
            if tool_name:
                result["current_tool"] = tool_name
                result["tool_input"] = tool_args
            
            return result
        
        except Exception as e:
            logger.error(f"Agent node error: {e}")
            return {
                "messages": messages,
                "iteration_count": iteration,
                "error": str(e),
                "error_count": state.get("error_count", 0) + 1
            }
    
    def tool_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Tool execution node.
        
        Executes the current_tool with tool_input and returns result.
        
        Args:
            state: Current agent state (must have current_tool and tool_input)
        
        Returns:
            State update with tool result added to messages and tool_results
        """
        tool_name = state.get("current_tool")
        tool_input = state.get("tool_input", {})
        messages = state["messages"]
        tool_results = state.get("tool_results", [])
        
        logger.debug(f"Tool node: executing {tool_name} with {tool_input}")
        
        # Fallback: If current_tool is missing (state issue), try to parse from last message
        if not tool_name and messages:
            last_msg = messages[-1]
            if hasattr(last_msg, 'content'):
                logger.info("Re-parsing last message for tool use in tool_node fallback")
                t_name, t_args = self._extract_tool_use(last_msg.content)
                if t_name:
                    tool_name = t_name
                    tool_input = t_args
        
        if not tool_name:
            logger.warning("Tool node called but no current_tool specified")
            return {
                "messages": messages,
                "tool_results": tool_results,
                "error": "No tool specified"
            }
        
        try:
            # Find and execute tool
            result = self._execute_tool(tool_name, tool_input)
            
            logger.debug(f"Tool result: {str(result)[:100]}")
            
            # Add tool result to messages
            tool_msg = ToolMessage(content=str(result), tool_call_id=tool_name)
            new_messages = messages + [tool_msg]
            
            # Track tool call
            self.tool_calls.append({
                "tool": tool_name,
                "args": tool_input,
                "result": result
            })
            self.add_reasoning_step(f"Tool result: {str(result)[:100]}")
            self.memory.add_tool_result(tool_name, result)
            
            # Accumulate tool results
            new_tool_results = tool_results + [{
                "tool": tool_name,
                "args": tool_input,
                "result": result
            }]
            
            return {
                "messages": new_messages,
                "tool_results": new_tool_results,
                "current_tool": None,
                "tool_input": None,
            }
        
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "messages": messages,
                "tool_results": tool_results,
                "error": str(e),
                "error_count": state.get("error_count", 0) + 1,
                "current_tool": None,
            }
    
    def router(self, state: AgentState) -> str:
        """
        Conditional router for state machine.
        
        Decides whether to:
        - Continue to tool_node (if tool use detected)
        - End (if final answer or max iterations reached)
        
        Args:
            state: Current agent state
        
        Returns:
            Route: "tool_node" or "__end__"
        """
        iteration = state["iteration_count"]
        max_iter = state["max_iterations"]
        
        # Check if max iterations reached
        if iteration >= max_iter:
            logger.info(f"Max iterations ({max_iter}) reached")
            return END
        
        # Check if a tool was identified in the previous step
        if state.get("current_tool"):
            return "tool_node"
        
        # No tool use - end
        return END
    
    def create_graph(self) -> StateGraph:
        """
        Create and compile the LangGraph state machine.
        
        Graph structure:
        START -> agent_node -> router -> {tool_node -> agent_node} or END
        
        Returns:
            Compiled StateGraph ready for execution
        """
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("agent", self.agent_node)
        graph.add_node("tool", self.tool_node)
        
        # Add edges
        graph.set_entry_point("agent")
        
        # agent -> router decides next step
        graph.add_conditional_edges(
            "agent",
            self.router,
            {
                "tool_node": "tool",
                END: END
            }
        )
        
        # After tool execution, go back to agent
        graph.add_edge("tool", "agent")
        
        logger.info("StateGraph created and compiled")
        
        return graph.compile()

    
    def execute(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> AgentExecutionResult:
        """
        Execute agent on prompt using the compiled LangGraph.
        
        Args:
            prompt: User prompt
            context: Additional context
        
        Returns:
            AgentExecutionResult with output and reasoning
        """
        # Reset state
        self.iteration_count = 0
        self.reasoning_steps = []
        self.tool_calls = []
        
        logger.info(f"Starting agent execution: {prompt[:50]}...")
        
        # Add to memory
        self.memory.add_human(prompt)
        
        try:
            # Create initial state
            initial_state = create_initial_state(max_iterations=self.max_iterations)
            
            # Educational/Multi-Agent System Prompt
            system_prompt = (
                "You are an advanced AI agent capable of multi-perspective reasoning. "
                "To solve complex problems effectively, adopt different PERSONAS. "
                "Start your thought process with '[Persona Name]:' to indicate which perspective you are using.\n"
                "Recommended Personas:\n"
                "- [Planner]: Decomposes the task.\n"
                "- [Researcher]: Looks up information (using tools).\n"
                "- [Analyst]: Synthesizes data.\n"
                "- [Critic]: Checks for errors.\n"
                "- [Finalizer]: Provides the answer.\n\n"
                "Example:\n"
                "[Planner]: I need to check the weather first.\n"
                "use_tool: weather_api with city='London'"
            )
            
            from langchain_core.messages import SystemMessage
            initial_state["messages"] = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            initial_state["context"] = context or {}
            
            # Create and run graph
            graph = self.create_graph()
            final_state = graph.invoke(initial_state)
            
            # Extract results from final state
            messages = final_state.get("messages", [])
            final_output = None
            
            # Get last message as final output
            if messages:
                last_msg = messages[-1]
                final_output = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            
            # Determine status
            status = "success"
            error = final_state.get("error")
            error_count = final_state.get("error_count", 0)
            
            if error:
                status = "error"
            elif final_state.get("iteration_count", 0) >= self.max_iterations:
                status = "incomplete"
            
            iterations = final_state.get("iteration_count", 0)
            
            logger.info(f"Agent execution completed: {iterations} iterations, status={status}")
            
            return AgentExecutionResult(
                status=status,
                final_output=final_output,
                reasoning_steps=self.reasoning_steps,
                tool_calls=self.tool_calls,
                iterations=iterations,
                error=error
            )
        
        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
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
    
    def _extract_persona(self, text: str) -> Optional[str]:
        """Extract persona tag like [Researcher]: ..."""
        match = re.search(r"^\s*\[([a-zA-Z\s]+)\]:", text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_tool_use(self, response_text: str) -> tuple[Optional[str], Optional[Dict]]:
        """
        Extract tool use from LLM response.
        
        Looks for patterns like:
        - "use_tool: extract_text_from_image with image_path=document.jpg"
        - "{\"tool\": \"extract_text_from_image\", \"args\": {...}}"
        
        Returns:
            Tuple of (tool_name, tool_args) or (None, None) if no tool detected
        """
        # Pattern 1: use_tool: name with args
        match = re.search(r"use_tool:\s*(\w+)\s*(?:with\s+(.+))?", response_text, re.IGNORECASE)
        if match:
            tool_name = match.group(1)
            args_str = match.group(2)
            args = {}
            if args_str:
                # Simplified robust parsing for the specific mock format: query="stuff"
                # Just extracts the content between the first pair of quotes found
                q_match = re.search(r'query=["\'](.+?)["\']', args_str)
                if q_match:
                    args["query"] = q_match.group(1)
                else:
                    # Fallback to splitting by space if no quotes
                    parts = args_str.split("=")
                    if len(parts) == 2:
                        args[parts[0].strip()] = parts[1].strip()
                        
            print(f"DEBUG: Detected tool use: {tool_name} args={args}") # Force print to stdout
            logger.warning(f"Detected tool use: {tool_name} args={args}") # Use warning to ensure visibility
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
        
        logger.info(f"No tool use detected in: '{response_text[:50]}...'")
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
