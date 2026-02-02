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

        mock_full_text = MagicMock()
        mock_full_text.description = "Extracted text from image"
        mock_full_text.confidence = 0  # text_detection returns 0 for full text
        
        # Individual symbols/words with confidence scores (>0)
        mock_symbol1 = MagicMock()
        mock_symbol1.confidence = 0.95
        mock_symbol2 = MagicMock()
        mock_symbol2.confidence = 0.93
        
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_full_text, mock_symbol1, mock_symbol2]
        mock_client.text_detection.return_value = mock_response

        # Create adapter and test
        ocr = GoogleVisionOCR()
        result = ocr.ocr_image("test_image.jpg")

        # Verify result
        assert result["text"] == "Extracted text from image"
        # Average of 0.95 and 0.93 = 0.94
        assert abs(result["confidence"] - 0.94) < 0.01

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
        """Test that OCR defaults to 1.0 when no positive confidence values available."""
        # Setup mock with zero confidence (typical for text_detection full annotation)
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_annotation = MagicMock()
        mock_annotation.description = "Text with no confidence"
        mock_annotation.confidence = 0  # text_detection returns 0
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_annotation]  # Only full text, no symbols
        mock_client.text_detection.return_value = mock_response

        # Create adapter and test
        ocr = GoogleVisionOCR()
        result = ocr.ocr_image("test_image.jpg")

        # Verify result - should default to 1.0 when confidence is 0 or missing
        assert result["text"] == "Text with no confidence"
        assert result["confidence"] == 1.0

    def test_ocr_with_invalid_image_path(self):
        """Test OCR with non-existent image file raises error."""
        ocr = GoogleVisionOCR()

        with pytest.raises(FileNotFoundError):
            ocr.ocr_image("non_existent_image.jpg")

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_returns_dict_with_correct_keys(self, mock_client_class):
        """Test that OCR result has expected keys and types."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_full_text = MagicMock()
        mock_full_text.description = "Sample text"
        mock_full_text.confidence = 0
        
        mock_symbol = MagicMock()
        mock_symbol.confidence = 0.85
        
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_full_text, mock_symbol]
        mock_client.text_detection.return_value = mock_response

        # Create adapter and test
        ocr = GoogleVisionOCR()
        result = ocr.ocr_image("test_image.jpg")

        # Verify keys and types
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
