import pytest
from agentic_platform.adapters import s3_artifact_store

def test_s3_artifact_store_adapter_inmemory():
    adapter = s3_artifact_store.S3ArtifactStoreAdapter()
    ref = adapter.put("job-123", {"foo": "bar"})
    assert ref.startswith("s3://job-123/")
    result = adapter.get(ref)
    assert result == {"foo": "bar"}
