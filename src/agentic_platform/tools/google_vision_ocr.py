import os
import logging
from typing import Any, Dict
from google.cloud import vision
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

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
        
        # Google Vision API returns confidence on the full_detection_confidence
        # For text_detection, we can get confidence from response properties
        # or calculate from the overall detection quality
        
        # Check if full annotation has confidence
        if hasattr(texts[0], 'confidence') and texts[0].confidence is not None:
            confidence = float(texts[0].confidence)
            logger.info(f"Using full text annotation confidence: {confidence}")
        else:
            # The text_detection response may have a full_detection_confidence
            # or we calculate from all detected symbols
            symbol_confidences = []
            for i, text in enumerate(texts[1:], 1):
                # Check for confidence attribute (may or may not exist)
                conf = getattr(text, 'confidence', None)
                if conf is not None:
                    symbol_confidences.append(float(conf))
                    logger.debug(f"Symbol {i}: confidence={conf}")
            
            if symbol_confidences:
                confidence = sum(symbol_confidences) / len(symbol_confidences)
                logger.info(f"Calculated confidence from {len(symbol_confidences)} symbols: {confidence}")
            else:
                # Google Vision doesn't always return confidence for text_detection
                # Default to 1.0 (high confidence) for detection, as Google Vision is generally very accurate
                confidence = 1.0
                logger.warning(f"No confidence scores available from API, using default: {confidence}")
        
        return {"text": full_text, "confidence": confidence}
