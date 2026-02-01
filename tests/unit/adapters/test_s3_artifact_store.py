import pytest
from agentic_platform.adapters import s3_artifact_store

def test_s3_artifact_store_adapter_stub():
    adapter = s3_artifact_store.S3ArtifactStoreAdapter()
    with pytest.raises(NotImplementedError):
        adapter.put("job-123", {"foo": "bar"})
    with pytest.raises(NotImplementedError):
        adapter.get("artifact-ref")
