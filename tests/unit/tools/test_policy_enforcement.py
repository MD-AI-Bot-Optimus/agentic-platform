import pytest
from agentic_platform.tools import model_router, policy

class DummyGPTClient:
    def __init__(self, model_name):
        self.model_name = model_name
    def call(self, prompt, args):
        return f"{self.model_name} response"

def test_tool_allowlist_policy_blocks_unauthorized():
    allowlist = ["gpt-4"]
    router = model_router.ModelRouter({
        "gpt-4": DummyGPTClient("gpt-4"),
        "gpt-3.5": DummyGPTClient("gpt-3.5"),
    })
    policy_enforcer = policy.ToolAllowlistPolicy(allowlist)
    node = {"id": "step1", "model": "gpt-3.5"}
    with pytest.raises(PermissionError):
        policy_enforcer.check(node)
    # Allowed model
    node2 = {"id": "step2", "model": "gpt-4"}
    policy_enforcer.check(node2)  # Should not raise
