import os
from typing import Any, Dict
from google.cloud import vision
from google.oauth2 import service_account

class GoogleVisionOCR:
    def __init__(self, credentials_json: str = None):
        if credentials_json:
            credentials = service_account.Credentials.from_service_account_file(credentials_json)
            self.client = vision.ImageAnnotatorClient(credentials=credentials)
        else:
            self.client = vision.ImageAnnotatorClient()

    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        with open(image_path, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        if not texts:
            return {"text": "", "confidence": 0.0}
        # The first annotation is the full text
        full_text = texts[0].description
        # Calculate average confidence from individual symbols (texts[1:])
        # texts[0] is the full text, texts[1:] are individual symbols/words
        symbol_confidences = [getattr(text, 'confidence', 1.0) for text in texts[1:] if hasattr(text, 'confidence')]
        if symbol_confidences:
            confidence = sum(symbol_confidences) / len(symbol_confidences)
        else:
            # Fallback: use 1.0 if no individual confidences are available
            confidence = 1.0
        return {"text": full_text, "confidence": confidence}
