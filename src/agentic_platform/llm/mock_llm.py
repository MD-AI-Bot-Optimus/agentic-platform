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
        
        # Handle both string input and message list input
        if isinstance(input, str):
            prompt_text = input
        elif isinstance(input, list) and len(input) > 0:
            last_message = input[-1]
            prompt_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            prompt_text = str(input)
        
        # Generate deterministic response
        response = self._generate_response(prompt_text)
        return AIMessage(content=response)
    
    def _generate_response(self, prompt: str) -> str:
        """Generate a mock response based on prompt."""
        prompt_lower = prompt.lower()
        
        # Simple pattern matching for deterministic responses
        if "ocr" in prompt_lower or "extract text" in prompt_lower:
            return "I'll extract text from the image using OCR. The image contains important business information with good clarity."
        elif "classify" in prompt_lower or "document type" in prompt_lower:
            return "I'll classify the document. Based on the content, this appears to be a business document like an invoice or contract."
        elif "sentiment" in prompt_lower or "emotion" in prompt_lower:
            return "The sentiment of this text is positive. The language used is professional and constructive."
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            return "Here's a summary: The document contains key information about business processes and agreements."
        elif "what is" in prompt_lower and "+" in prompt_lower:
            # Simple math
            if "2+2" in prompt or "2 + 2" in prompt:
                return "2 + 2 = 4"
            return "The result is calculated correctly."
        else:
            return "I understand your request and I'm ready to help process documents and extract information as needed."
    
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
    
    def _generate_response(self, prompt: str) -> str:
        """Get varied mock response."""
        import random
        responses = [
            "Mock response variant 1: Analysis complete.",
            "Mock response variant 2: Processing successful.",
            "Mock response variant 3: Task completed.",
            super()._generate_response(prompt),  # Also include base response sometimes
        ]
        return random.choice(responses)
