import time
from typing import Dict, Any
from .base import OCRProvider
# Import the actual implementation if available, or just mock the dependency if not strictly needed here
# For now we will import the original class inside the factory or use a wrapper here if we want to reuse code.
# Ideally we move the logic from 'tools/google_vision_ocr.py' to here or wrap it.
# Let's import it to wrap it.
try:
    from ..tools.google_vision_ocr import GoogleVisionOCR as OriginalGoogleOCR
except ImportError:
    OriginalGoogleOCR = None

class MockOCR(OCRProvider):
    """
    Local mock OCR for testing without API costs/credentials.
    """
    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        return {
            "text": f"[MOCK OCR] Extracted text from {image_path}.\nThis is a simulated result for testing purposes.",
            "blocks": [
                {"text": "MOCK HEADER", "confidence": 0.99},
                {"text": "Simulated body text content.", "confidence": 0.95}
            ]
        }

class GoogleCloudVisionOCR(OCRProvider):
    """
    Production implementation using Google Cloud Vision API.
    """
    def __init__(self, credentials_json: str = None):
        if OriginalGoogleOCR:
            self.client = OriginalGoogleOCR(credentials_json)
        else:
            raise ImportError("GoogleVisionOCR module not found.")

    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        return self.client.ocr_image(image_path)
