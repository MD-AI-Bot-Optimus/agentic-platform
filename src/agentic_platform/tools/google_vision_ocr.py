import os
import logging
from typing import Any, Dict
from google.cloud import vision
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class GoogleVisionOCR:
    def __init__(self, credentials_json: str = None):
        try:
            if credentials_json:
                credentials = service_account.Credentials.from_service_account_file(credentials_json)
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
            else:
                self.client = vision.ImageAnnotatorClient()
        except Exception as e:
            logger.warning(f"Failed to initialize Google Vision client: {e}")
            self.client = None

    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        try:
            if self.client is None:
                return {"text": "", "confidence": 0.0, "error": "Google Vision client not initialized - check credentials"}
            
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
            confidence_source = "default"
            
            # Try to get confidence from full annotation (usually 0 or missing for text_detection)
            full_conf = getattr(texts[0], 'confidence', None)
            if full_conf is not None and full_conf > 0:
                confidence = float(full_conf)
                confidence_source = "full_text_annotation"
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
                    confidence_source = f"avg_of_{len(symbol_confidences)}_symbols"
                    logger.info(f"Calculated confidence from {len(symbol_confidences)} symbols: {confidence:.4f}")
                else:
                    # For complex layouts with many symbols but no confidence data,
                    # use text extraction completeness as fallback metric
                    total_symbols = len(texts) - 1
                    if total_symbols > 150:
                        # Complex document (table, form, etc.) - more difficult for OCR
                        # But if text extracted, Google Vision succeeded, so higher confidence
                        confidence = 0.95  # Slightly reduced from 1.0 for complex layouts
                        confidence_source = f"complex_layout_{total_symbols}_symbols"
                        logger.info(f"Complex layout detected ({total_symbols} symbols, 0 confidence scores). Using {confidence} for difficulty factor.")
                    else:
                        confidence_source = f"default_simple_layout"
                        logger.debug(f"No positive confidence values from {total_symbols} symbols, using default")
            
            # Ensure confidence is a float and within valid range [0.0, 1.0]
            confidence = float(max(0.0, min(1.0, confidence)))
            logger.debug(f"Final confidence: {confidence:.4f} (source: {confidence_source})")
            
            return {"text": full_text, "confidence": confidence}
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {str(e)}", exc_info=True)
            return {"text": "", "confidence": 0.0, "error": str(e)}
