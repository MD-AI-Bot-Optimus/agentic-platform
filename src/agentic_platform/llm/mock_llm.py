"""
Mock LLM for testing without API costs.

Provides deterministic, configurable LLM responses for:
- Unit testing
- Integration testing
- Development
- Cost-free testing

Usage:
    from agentic_platform.llm.mock_llm import MockLLM
    
    mock_llm = MockLLM(model="mock-llm")
    response = mock_llm.invoke("What is 2 + 2?")
    # Returns: AIMessage(content="4")
"""

import logging
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.runnables import Runnable

logger = logging.getLogger(__name__)


class MockLLM(Runnable):
    """Mock LLM that returns predefined responses for testing."""
    
    @property
    def InputType(self):
        """Input type for the runnable."""
        return List[BaseMessage]
    
    @property
    def OutputType(self):
        """Output type for the runnable."""
        return AIMessage
    
    def __init__(self, model: str = "mock-llm", deterministic: bool = True, **kwargs):
        """
        Initialize mock LLM.
        
        Args:
            model: Model name (for identification)
            deterministic: If True, always return same response for same input
            **kwargs: Additional arguments (ignored)
        """
        super().__init__(**kwargs)
        self.model = model
        self.deterministic = deterministic
        self._call_count = 0
        logger.info(f"Initialized MockLLM (deterministic={deterministic})")
    
    
    def invoke(self, input: Any, config=None) -> AIMessage:
        """Invoke the mock LLM."""
        self._call_count += 1
        
        # Determine strict prompt text but pass full context if available
        messages = []
        if isinstance(input, list):
            messages = input
            last_message = input[-1]
            prompt_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            prompt_text = str(input)
        
        # Generate response based on full context (to detect tool outputs)
        response = self._generate_response(prompt_text, messages)
        return AIMessage(content=response)
    
    def _generate_response(self, prompt: str, messages: List[Any] = None) -> str:
        """
        Generate a mock response based on prompt and context.
        
        Simulates:
        1. Planning (deciding to use a tool)
        2. Answering (using tool output)
        """
        prompt_lower = prompt.lower()
        messages = messages or []
        
        # Check if we just received a tool output
        last_msg = messages[-1] if messages else None
        is_tool_output = hasattr(last_msg, 'tool_call_id') or (isinstance(last_msg, dict) and last_msg.get("type") == "tool")
        
        # Scenario 1: Final Answer (Pass 2 - After Tool Execution)
        if is_tool_output:
            return self._generate_final_answer(last_msg.content)
            
        # Scenario 2: Decide to use Tool (Pass 1 - Initial Prompt)
        # We simulate tool use for "what is..." questions to show the graph animation
        if "what is" in prompt_lower or "explain" in prompt_lower:
            return f'use_tool: search_knowledge_base with query="{prompt}"'
            
        # Fallback: Immediate knowledge-based answer (No tool)
        return self._generate_knowledge_answer(prompt)

    def _generate_final_answer(self, tool_output: str) -> str:
        """Generate final answer based on tool output and model persona."""
        prefix = ""
        if "gemini-2.0-flash" in self.model:
            prefix = "⚡ [Gemini 2.0 Flash] Speedily analyzed: "
        elif "gemini-1.5-pro" in self.model:
            prefix = "🧠 [Gemini 1.5 Pro] Deep contextual analysis: "
        else:
            prefix = "MOCK ANSWER: "
            
        return f"{prefix}Based on the knowledge base search, {tool_output} I hope this detailed explanation helps!"

    def _generate_knowledge_answer(self, prompt: str) -> str:
        """Generate a static knowledge answer without tool use."""
        prompt_lower = prompt.lower()
        if "ocr" in prompt_lower:
            return "I'll extract text from the image using OCR. The image contains important business information."
        elif "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm the LangGraph Agent demo. Ask me 'What is a neural network?' to see me use my tools!"
        else:
            return (f"MOCK ANSWER: I received your request: '{prompt}'. "
                    "Try asking 'What is [topic]?' to see multi-step reasoning in action!")

    def batch(self, inputs, config=None, **kwargs):
        """Batch invoke the mock LLM."""
        return [self.invoke(input_item, config) for input_item in inputs]


class DeterministicMockLLM(MockLLM):
    """
    Deterministic Mock LLM that returns exact responses for testing.
    
    All calls with same input return same output.
    """
    
    def __init__(self, model: str = "mock-llm-deterministic", **kwargs):
        super().__init__(model=model, deterministic=True, **kwargs)


class RandomMockLLM(MockLLM):
    """
    Random Mock LLM that returns varied responses.
    
    Useful for testing robustness to different outputs.
    """
    
    def __init__(self, model: str = "mock-llm-random", **kwargs):
        super().__init__(model=model, deterministic=False, **kwargs)
    
    def _generate_response(self, prompt: str, messages: List[Any] = None) -> str:
        """Get varied mock response."""
        import random
        # Just delegate to basic string logic for random mock for now to avoid complexity
        base = super()._generate_knowledge_answer(prompt)
        responses = [
            f"Variant A: {base}",
            f"Variant B: {base}",
            base
        ]
        return random.choice(responses)
