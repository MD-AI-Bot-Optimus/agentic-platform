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
        
        # Google Vision text_detection API does not reliably provide confidence
        # The confidence field on annotations may be 0 or missing
        # Since Google Vision is highly accurate for text detection, we default to 1.0
        # unless we can extract a meaningful confidence value
        
        confidence = 1.0  # Default for text_detection
        
        # Try to get confidence from full annotation (usually 0 or missing for text_detection)
        full_conf = getattr(texts[0], 'confidence', None)
        if full_conf is not None and full_conf > 0:
            confidence = float(full_conf)
            logger.info(f"Using full text annotation confidence: {confidence}")
        
        # Try to get confidence from individual symbols
        if confidence == 1.0 and len(texts) > 1:
            symbol_confidences = []
            for i, text in enumerate(texts[1:], 1):
                conf = getattr(text, 'confidence', None)
                if conf is not None and conf > 0:
                    symbol_confidences.append(float(conf))
                    logger.debug(f"Symbol {i}: confidence={conf}")
            
            if symbol_confidences:
                confidence = sum(symbol_confidences) / len(symbol_confidences)
                logger.info(f"Calculated confidence from {len(symbol_confidences)} symbols: {confidence:.4f}")
            else:
                logger.debug(f"No positive confidence values from {len(texts)-1} symbols, using default")
        
        # Ensure confidence is a float and within valid range [0.0, 1.0]
        confidence = float(max(0.0, min(1.0, confidence)))
        
        return {"text": full_text, "confidence": confidence}
