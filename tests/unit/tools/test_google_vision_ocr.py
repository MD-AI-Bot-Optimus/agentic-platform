"""
Unit tests for GoogleVisionOCR adapter.

Tests the OCR functionality with mocked Google Vision API responses.
"""

import pytest
from unittest.mock import MagicMock, patch
from agentic_platform.tools.google_vision_ocr import GoogleVisionOCR


class TestGoogleVisionOCR:
    """Tests for GoogleVisionOCR adapter."""

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_with_valid_image(self, mock_client_class):
        """Test OCR extraction with mocked Google Vision API."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_annotation = MagicMock()
        mock_annotation.description = "Extracted text from image"
        mock_annotation.score = 0.95
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_annotation]
        mock_client.text_detection.return_value = mock_response

        # Create adapter and test
        ocr = GoogleVisionOCR()
        result = ocr.ocr_image("test_image.jpg")

        # Verify result
        assert result["text"] == "Extracted text from image"
        assert result["confidence"] == 0.95

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_with_no_text(self, mock_client_class):
        """Test OCR when no text is detected."""
        # Setup mock with no text annotations
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text_annotations = []
        mock_client.text_detection.return_value = mock_response

        # Create adapter and test
        ocr = GoogleVisionOCR()
        result = ocr.ocr_image("blank_image.jpg")

        # Verify result
        assert result["text"] == ""
        assert result["confidence"] == 0.0

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_default_confidence(self, mock_client_class):
        """Test that OCR uses default confidence of 1.0 when score is missing."""
        # Setup mock without score attribute
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_annotation = MagicMock(spec=["description"])  # No 'score' attribute
        mock_annotation.description = "Text without score"
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_annotation]
        mock_client.text_detection.return_value = mock_response

        # Create adapter and test
        ocr = GoogleVisionOCR()
        result = ocr.ocr_image("test_image.jpg")

        # Verify result
        assert result["text"] == "Text without score"
        assert result["confidence"] == 1.0  # Default confidence

    def test_ocr_with_invalid_image_path(self):
        """Test OCR with non-existent image file raises error."""
        ocr = GoogleVisionOCR()

        with pytest.raises(FileNotFoundError):
            ocr.ocr_image("non_existent_image.jpg")

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_returns_dict_with_correct_keys(self, mock_client_class):
        """Test that OCR result has expected keys."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_annotation = MagicMock()
        mock_annotation.description = "Sample text"
        mock_annotation.score = 0.85
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_annotation]
        mock_client.text_detection.return_value = mock_response

        # Create adapter and test
        ocr = GoogleVisionOCR()
        result = ocr.ocr_image("test_image.jpg")

        # Verify keys
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert len(result) == 2  # Only these two keys


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
