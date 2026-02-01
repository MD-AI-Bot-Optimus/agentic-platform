import pytest
from agentic_platform.agents import artifact_store, base
import hashlib
import json

def compute_hash(artifact):
    # Deterministic hash for test
    return hashlib.sha256(json.dumps(artifact, sort_keys=True).encode()).hexdigest()

def test_artifact_hashing_and_versioning():
    store = artifact_store.InMemoryArtifactStore()
    agent = base.Agent(name="ocr", version="v1")
    artifact = {"foo": "bar"}
    # Save artifact and compute hash
    ref = store.put(agent.name + ":" + agent.version, artifact)
    artifact_hash = compute_hash(artifact)
    # Simulate versioned output: ref includes hash
    assert artifact_hash in ref or artifact_hash == ref
    # (Implementation should update ref to include hash)
