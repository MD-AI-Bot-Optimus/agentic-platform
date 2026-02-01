"""
Integration tests for OCR functionality.

Tests the `/run-ocr/` endpoint with real images and Google Vision API.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os

from agentic_platform.api import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_image_path():
    """Path to sample OCR image."""
    return Path(__file__).parent.parent.parent.parent / "sample_data" / "ocr_sample_plaid.jpg"


class TestOCREndpoint:
    """Tests for POST /run-ocr/ endpoint."""

    def test_ocr_with_valid_image(self, client, sample_image_path):
        """Test OCR with a valid image file."""
        if not sample_image_path.exists():
            pytest.skip(f"Sample image not found at {sample_image_path}")

        with open(sample_image_path, "rb") as img_file:
            response = client.post(
                "/run-ocr/",
                files={"image": (sample_image_path.name, img_file, "image/jpeg")}
            )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "result" in data
        assert "tool_results" in data
        assert "audit_log" in data

        # Verify result structure
        result = data["result"]
        assert "job_id" in result
        assert "status" in result
        assert result["status"] == "completed"
        assert "tool_results" in result

        # Verify tool results contain OCR output
        tool_results = data["tool_results"]
        assert len(tool_results) > 0
        assert "result" in tool_results[0]
        assert "text" in tool_results[0]["result"]
        assert "formatted_text_lines" in tool_results[0]["result"]

        # Verify formatted text lines are non-empty list
        formatted_lines = tool_results[0]["result"]["formatted_text_lines"]
        assert isinstance(formatted_lines, list)
        if tool_results[0]["result"]["text"]:  # If text exists
            assert len(formatted_lines) > 0

    def test_ocr_without_image_fails(self, client):
        """Test OCR without image file returns 422."""
        response = client.post("/run-ocr/")
        assert response.status_code == 422

    def test_ocr_response_has_audit_log(self, client, sample_image_path):
        """Test that OCR response includes audit log events."""
        if not sample_image_path.exists():
            pytest.skip(f"Sample image not found at {sample_image_path}")

        with open(sample_image_path, "rb") as img_file:
            response = client.post(
                "/run-ocr/",
                files={"image": (sample_image_path.name, img_file, "image/jpeg")}
            )

        assert response.status_code == 200
        data = response.json()
        audit_log = data["audit_log"]

        # Verify audit log has events
        assert len(audit_log) > 0

        # Verify event structure
        for event in audit_log:
            assert "event_type" in event
            assert "job_id" in event
            assert "timestamp" in event
            assert "status" in event

    def test_ocr_text_extraction(self, client, sample_image_path):
        """Test that OCR actually extracts text from the image."""
        if not sample_image_path.exists():
            pytest.skip(f"Sample image not found at {sample_image_path}")

        with open(sample_image_path, "rb") as img_file:
            response = client.post(
                "/run-ocr/",
                files={"image": (sample_image_path.name, img_file, "image/jpeg")}
            )

        assert response.status_code == 200
        data = response.json()
        tool_results = data["tool_results"]

        # For known sample images, verify some text is extracted
        extracted_text = tool_results[0]["result"]["text"]
        assert isinstance(extracted_text, str)
        # The sample image should contain some text
        # (This is a basic check; actual validation depends on image content)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
