import pytest
from agentic_platform.agents import artifact_store, base
from agentic_platform.audit import audit_log

def test_agent_output_linked_to_audit():
    store = artifact_store.InMemoryArtifactStore()
    log = audit_log.InMemoryAuditLog()
    agent = base.Agent(name="ocr", version="v1")
    artifact = {"foo": "bar"}
    ref = store.put(agent.name + ":" + agent.version, artifact)
    # Simulate audit event linking
    event = log.emit_event_with_artifact(agent, ref)
    assert event.artifact_ref == ref
    assert event.agent_name == agent.name
    assert event.agent_version == agent.version
