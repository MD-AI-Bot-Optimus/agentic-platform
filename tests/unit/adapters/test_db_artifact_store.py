import pytest
from agentic_platform.adapters import db_artifact_store

def test_db_artifact_store_adapter_stub():
    adapter = db_artifact_store.DBArtifactStoreAdapter()
    with pytest.raises(NotImplementedError):
        adapter.put("job-123", {"foo": "bar"})
    with pytest.raises(NotImplementedError):
        adapter.get("artifact-ref")
