import pytest
from agentic_platform.tools import model_router

class DummyGPTClient:
    def __init__(self, model_name):
        self.model_name = model_name
    def call(self, prompt, args):
        return f"{self.model_name} response"

def test_model_selection_per_node():
    router = model_router.ModelRouter({
        "gpt-4": DummyGPTClient("gpt-4"),
        "gpt-3.5": DummyGPTClient("gpt-3.5"),
    })
    # Node/task specifies model
    node = {"id": "step1", "model": "gpt-4"}
    result = router.call(node, prompt="Hello", args={})
    assert result == "gpt-4 response"
    node2 = {"id": "step2", "model": "gpt-3.5"}
    result2 = router.call(node2, prompt="Hi", args={})
    assert result2 == "gpt-3.5 response"
    # Default fallback
    node3 = {"id": "step3"}
    result3 = router.call(node3, prompt="Hey", args={})
    assert result3 == "gpt-4 response"  # default is gpt-4
