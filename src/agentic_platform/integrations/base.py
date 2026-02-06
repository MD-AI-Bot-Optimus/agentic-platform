from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class KnowledgeBaseProvider(ABC):
    """Abstract base class for Knowledge Base providers."""
    
    @abstractmethod
    def search(self, query: str) -> str:
        """Search the knowledge base for the given query."""
        pass

class OCRProvider(ABC):
    """Abstract base class for OCR providers."""
    
    @abstractmethod
    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        """Perform OCR on the given image path."""
        pass
