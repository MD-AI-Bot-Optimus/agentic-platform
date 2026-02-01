import pytest
from agentic_platform.agents import registry

class DummyAgent:
    def __init__(self, name, version):
        self.name = name
        self.version = version

def test_agent_registry_register_and_lookup():
    reg = registry.InMemoryAgentRegistry()
    agent = DummyAgent("ocr", "v1")
    reg.register(agent)
    found = reg.get("ocr", "v1")
    assert found is agent
    all_agents = reg.list()
    assert agent in all_agents

def test_agent_registry_duplicate_registration():
    reg = registry.InMemoryAgentRegistry()
    agent = DummyAgent("ocr", "v1")
    reg.register(agent)
    with pytest.raises(ValueError):
        reg.register(agent)  # Duplicate should raise
