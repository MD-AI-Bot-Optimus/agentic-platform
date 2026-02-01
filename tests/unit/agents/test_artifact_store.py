import pytest
from agentic_platform.agents import artifact_store

def test_artifact_store_put_and_get():
    store = artifact_store.InMemoryArtifactStore()
    job_id = "job-123"
    artifact = {"foo": "bar"}
    ref = store.put(job_id, artifact)
    loaded = store.get(ref)
    assert loaded == artifact

def test_artifact_store_duplicate_put():
    store = artifact_store.InMemoryArtifactStore()
    job_id = "job-123"
    artifact = {"foo": "bar"}
    ref1 = store.put(job_id, artifact)
    with pytest.raises(ValueError):
        store.put(job_id, artifact)  # Duplicate put for same job_id should fail
