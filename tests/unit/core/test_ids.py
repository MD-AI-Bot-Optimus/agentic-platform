import pytest

from platform.core import ids

def test_job_id_generation():
    job_id = ids.generate_job_id()
    assert isinstance(job_id, str)
    assert len(job_id) > 0
    # Should look like a UUID
    assert '-' in job_id

def test_correlation_id_generation():
    correlation_id = ids.generate_correlation_id()
    assert isinstance(correlation_id, str)
    assert len(correlation_id) > 0
    assert '-' in correlation_id
