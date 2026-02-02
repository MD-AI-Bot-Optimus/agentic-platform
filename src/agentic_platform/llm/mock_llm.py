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
from langchain_core.language_model.llm import LLM
from langchain_core.outputs.llm_result import LLMResult

logger = logging.getLogger(__name__)


class MockLLM(LLM):
    """Mock LLM that returns predefined responses for testing."""
    
    model: str = "mock-llm"
    
    # Predefined responses for common prompts
    MOCK_RESPONSES = {
        "analyze": "Mock analysis complete. The document contains important information.",
        "summarize": "Mock summary: This is a concise summary of the provided text.",
        "extract": "Mock extraction: Key data extracted successfully.",
        "classify": "Mock classification: Document classified as 'general'.",
        "translate": "Mock translation: Translated to target language.",
    }
    
    # Tool call patterns
    TOOL_CALLS = [
        {
            "name": "google_vision_ocr",
            "args": {"image_path": "document.jpg"},
            "result": {
                "text": "Mock OCR: Extracted text from image",
                "confidence": 0.95,
                "symbols_count": 150
            }
        }
    ]
    
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
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate mock response."""
        self._call_count += 1
        
        # Extract last message content
        last_message = messages[-1].content if messages else ""
        
        # Determine response based on message content
        response_content = self._get_mock_response(last_message)
        
        logger.debug(f"Mock LLM call #{self._call_count}: '{last_message[:50]}...' → '{response_content[:50]}...'")
        
        # Return as LLMResult
        from langchain_core.outputs import Generation
        return LLMResult(generations=[[Generation(text=response_content)]])
    
    def _get_mock_response(self, prompt: str) -> str:
        """Get mock response based on prompt content."""
        prompt_lower = prompt.lower()
        
        # Check for common keywords
        for keyword, response in self.MOCK_RESPONSES.items():
            if keyword in prompt_lower:
                return response
        
        # Check for tool use patterns
        if "call_tool" in prompt_lower or "invoke" in prompt_lower:
            tool_call = self.TOOL_CALLS[self._call_count % len(self.TOOL_CALLS)]
            return f"Mock tool call: {tool_call['name']} → {tool_call['result']}"
        
        # Default response
        if "?" in prompt:
            return "Mock LLM response: This is a deterministic mock response to your question."
        else:
            return "Mock LLM response: This is a deterministic mock response to your prompt."
    
    def invoke(self, input: str, **kwargs: Any) -> AIMessage:
        """Invoke mock LLM and return AIMessage."""
        response = self._get_mock_response(input)
        return AIMessage(content=response)
    
    @property
    def _llm_type(self) -> str:
        """Return LLM type identifier."""
        return "mock"
    
    def reset(self):
        """Reset call counter."""
        self._call_count = 0
        logger.info("MockLLM call counter reset")


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
    
    def _get_mock_response(self, prompt: str) -> str:
        """Get varied mock response."""
        import random
        responses = [
            "Mock response variant 1.",
            "Mock response variant 2.",
            "Mock response variant 3.",
            super()._get_mock_response(prompt),  # Also include base response sometimes
        ]
        return random.choice(responses)
