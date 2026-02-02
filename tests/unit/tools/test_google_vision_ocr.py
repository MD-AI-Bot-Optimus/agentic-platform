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
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
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
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
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
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
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
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
            result = ocr.ocr_image("test_image.jpg")

        # Verify keys and types
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_confidence_is_float_not_int(self, mock_client_class):
        """Test that confidence is always returned as float, never int."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_full_text = MagicMock()
        mock_full_text.description = "Text"
        mock_full_text.confidence = 0
        
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_full_text]
        mock_client.text_detection.return_value = mock_response

        ocr = GoogleVisionOCR()
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
            result = ocr.ocr_image("test.jpg")

        # Critical: must be float, not int
        assert isinstance(result["confidence"], float), f"Expected float, got {type(result['confidence'])}"
        assert result["confidence"] == 1.0

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_intermediate_confidence_value(self, mock_client_class):
        """Test that confidence can have intermediate values between 0 and 1."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_full_text = MagicMock()
        mock_full_text.description = "Sample text"
        mock_full_text.confidence = 0
        
        # Single symbol with intermediate confidence
        mock_symbol = MagicMock()
        mock_symbol.confidence = 0.42  # Specific intermediate value
        
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_full_text, mock_symbol]
        mock_client.text_detection.return_value = mock_response

        ocr = GoogleVisionOCR()
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
            result = ocr.ocr_image("test.jpg")

        # Should return the exact intermediate value
        assert isinstance(result["confidence"], float)
        assert result["confidence"] == 0.42
        assert 0.0 < result["confidence"] < 1.0

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_average_confidence_from_multiple_symbols(self, mock_client_class):
        """Test that confidence averages multiple symbol confidences correctly."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_full_text = MagicMock()
        mock_full_text.description = "Multi-symbol text"
        mock_full_text.confidence = 0
        
        # Multiple symbols with different confidence values
        symbols = []
        confidences = [0.75, 0.85, 0.65, 0.90, 0.72]
        for conf in confidences:
            mock_sym = MagicMock()
            mock_sym.confidence = conf
            symbols.append(mock_sym)
        
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_full_text] + symbols
        mock_client.text_detection.return_value = mock_response

        ocr = GoogleVisionOCR()
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
            result = ocr.ocr_image("test.jpg")

        # Should return average: (0.75 + 0.85 + 0.65 + 0.90 + 0.72) / 5 = 0.774
        expected_avg = sum(confidences) / len(confidences)
        assert isinstance(result["confidence"], float)
        assert abs(result["confidence"] - expected_avg) < 0.001
        assert 0.0 < result["confidence"] < 1.0

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_high_confidence_values(self, mock_client_class):
        """Test OCR with high confidence symbol values."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_full_text = MagicMock()
        mock_full_text.description = "High quality text"
        mock_full_text.confidence = 0
        
        # High confidence symbols
        symbols = []
        for conf in [0.98, 0.99, 0.97]:
            mock_sym = MagicMock()
            mock_sym.confidence = conf
            symbols.append(mock_sym)
        
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_full_text] + symbols
        mock_client.text_detection.return_value = mock_response

        ocr = GoogleVisionOCR()
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
            result = ocr.ocr_image("test.jpg")

        # High average but not exactly 1.0
        assert isinstance(result["confidence"], float)
        assert 0.95 < result["confidence"] < 1.0

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_low_confidence_values(self, mock_client_class):
        """Test OCR with low confidence symbol values."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_full_text = MagicMock()
        mock_full_text.description = "Low quality text"
        mock_full_text.confidence = 0
        
        # Low confidence symbols (but not zero, which would be ignored)
        symbols = []
        for conf in [0.15, 0.25, 0.20]:
            mock_sym = MagicMock()
            mock_sym.confidence = conf
            symbols.append(mock_sym)
        
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_full_text] + symbols
        mock_client.text_detection.return_value = mock_response

        ocr = GoogleVisionOCR()
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
            result = ocr.ocr_image("test.jpg")

        # Low average
        assert isinstance(result["confidence"], float)
        assert 0.0 < result["confidence"] < 0.3

    @patch("agentic_platform.tools.google_vision_ocr.vision.ImageAnnotatorClient")
    def test_ocr_mixed_zero_and_nonzero_confidence(self, mock_client_class):
        """Test that zero confidence symbols are ignored, only positive ones are averaged."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_full_text = MagicMock()
        mock_full_text.description = "Mixed confidence"
        mock_full_text.confidence = 0
        
        # Mix of zero and positive confidences
        symbols = []
        mock_sym1 = MagicMock()
        mock_sym1.confidence = 0  # Should be ignored
        symbols.append(mock_sym1)
        
        mock_sym2 = MagicMock()
        mock_sym2.confidence = 0.80  # Should be included
        symbols.append(mock_sym2)
        
        mock_sym3 = MagicMock()
        mock_sym3.confidence = 0.60  # Should be included
        symbols.append(mock_sym3)
        
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_full_text] + symbols
        mock_client.text_detection.return_value = mock_response

        ocr = GoogleVisionOCR()
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b''))), __exit__=MagicMock(return_value=None)))):
            result = ocr.ocr_image("test.jpg")

        # Average of only positive values: (0.80 + 0.60) / 2 = 0.70
        assert isinstance(result["confidence"], float)
        assert abs(result["confidence"] - 0.70) < 0.001
        assert 0.0 < result["confidence"] < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
