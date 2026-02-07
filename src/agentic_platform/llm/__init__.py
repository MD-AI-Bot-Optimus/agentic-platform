"""
LLM Provider Configuration and Factory

Supports multiple LLM providers:
- Anthropic (Claude 3.5 Sonnet, 3 Opus)
- OpenAI (GPT-4, GPT-4 Turbo)
- Google Vertex AI (Gemini 1.5 Pro, Gemini 2)

Usage:
    from agentic_platform.llm import get_llm_model, LLMProvider
    
    # Get default model
    llm = get_llm_model()
    
    # Get specific model
    llm = get_llm_model(model="gpt-4-turbo", provider="openai")
    
    # List available models
    models = list_available_models()
"""

import os
import logging
from enum import Enum
from typing import Optional, Dict, Any, List

# Trigger reload for new dependencies
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    MOCK = "mock"


class LLMConfig:
    """LLM Configuration management."""
    
    # Available models by provider
    MODELS = {
        LLMProvider.ANTHROPIC: [
            "claude-3.5-sonnet",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku"
        ],
        LLMProvider.OPENAI: [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ],
        LLMProvider.GOOGLE: [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-pro-latest",
            "gemini-flash-latest",
            "gemini-2",
            "gemini-3-pro",
            "gemini-3-pro-preview",
        ],
        LLMProvider.MOCK: [
            "mock-llm"
        ]
    }
    
    # Default models
    DEFAULT_MODELS = {
        LLMProvider.ANTHROPIC: "claude-3.5-sonnet",
        LLMProvider.OPENAI: "gpt-4-turbo",
        LLMProvider.GOOGLE: "gemini-flash-latest",
        LLMProvider.MOCK: "mock-llm"
    }
    
    # API Keys
    API_KEYS = {
        LLMProvider.ANTHROPIC: os.getenv("ANTHROPIC_API_KEY"),
        LLMProvider.OPENAI: os.getenv("OPENAI_API_KEY"),
        LLMProvider.GOOGLE: os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    }
    
    @classmethod
    def get_default_model(cls) -> tuple[LLMProvider, str]:
        """Get default LLM provider and model."""
        # Check environment variable
        default_model = os.getenv("LLM_DEFAULT_MODEL", "claude-3.5-sonnet")
        
        # Determine provider from model name
        for provider, models in cls.MODELS.items():
            if default_model in models:
                return provider, default_model
        
        # Fallback to Anthropic
        logger.warning(f"Unknown model {default_model}, using {cls.DEFAULT_MODELS[LLMProvider.ANTHROPIC]}")
        return LLMProvider.ANTHROPIC, cls.DEFAULT_MODELS[LLMProvider.ANTHROPIC]
    
    @classmethod
    def get_model(cls, model: Optional[str] = None, provider: Optional[str] = None) -> tuple[LLMProvider, str]:
        """Get LLM provider and model."""
        if model and provider:
            # Both specified
            try:
                prov = LLMProvider(provider.lower())
                if model not in cls.MODELS[prov]:
                    raise ValueError(f"Model {model} not available for provider {provider}")
                return prov, model
            except ValueError as e:
                logger.error(f"Invalid provider or model: {e}")
                return cls.get_default_model()
        
        elif model:
            # Only model specified - find provider
            for prov, models in cls.MODELS.items():
                if model in models:
                    return prov, model
            logger.warning(f"Model {model} not found, using default")
            return cls.get_default_model()
        
        elif provider:
            # Only provider specified - use default model for that provider
            try:
                prov = LLMProvider(provider.lower())
                return prov, cls.DEFAULT_MODELS[prov]
            except ValueError:
                logger.error(f"Invalid provider: {provider}")
                return cls.get_default_model()
        
        else:
            # None specified - use default
            return cls.get_default_model()
    
    @classmethod
    def list_available_models(cls) -> Dict[str, List[str]]:
        """List all available models by provider."""
        return {
            provider.value: models 
            for provider, models in cls.MODELS.items()
        }
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validate that required API keys are configured."""
        status = {}
        for provider, key in cls.API_KEYS.items():
            status[provider.value] = bool(key)
            if not key:
                logger.warning(f"API key not configured for {provider.value}")
        return status


def get_llm_model(model: Optional[str] = None, provider: Optional[str] = None) -> Any:
    """
    Factory function to get LLM model instance.
    
    Args:
        model: Model name (e.g., "claude-3.5-sonnet", "gpt-4-turbo")
        provider: Provider name (e.g., "anthropic", "openai", "google")
    
    Returns:
        LLM model instance ready to use
    
    Raises:
        ValueError: If provider is not configured or API key is missing
    """
    prov, model_name = LLMConfig.get_model(model, provider)
    
    # Check if mock is requested
    if os.getenv("LANGGRAPH_USE_MOCK_LLM", "false").lower() == "true" or prov == LLMProvider.MOCK:
        from agentic_platform.llm.mock_llm import MockLLM
        logger.info(f"Using mock LLM for testing (model: {model_name})")
        return MockLLM(model=model_name)
    
    # Get real LLM based on provider
    if prov == LLMProvider.ANTHROPIC:
        try:
            from langchain_anthropic import ChatAnthropic
            api_key = LLMConfig.API_KEYS[LLMProvider.ANTHROPIC]
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            logger.info(f"Using Anthropic Claude (model: {model_name})")
            return ChatAnthropic(model=model_name, api_key=api_key)
        except ImportError:
            raise ValueError("langchain-anthropic not installed. Install with: pip install langchain-anthropic")
    
    elif prov == LLMProvider.OPENAI:
        try:
            from langchain_openai import ChatOpenAI
            api_key = LLMConfig.API_KEYS[LLMProvider.OPENAI]
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            logger.info(f"Using OpenAI GPT (model: {model_name})")
            return ChatOpenAI(model=model_name, api_key=api_key)
        except ImportError:
            raise ValueError("langchain-openai not installed. Install with: pip install langchain-openai")
    
    elif prov == LLMProvider.GOOGLE:
        # Try Vertex AI first (Enterprise) - ONLY if credentials file actually exists
        gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if os.getenv("GCP_PROJECT_ID") and gcp_creds and os.path.exists(gcp_creds):
            try:
                from langchain_google_vertexai import ChatVertexAI
                logger.info(f"Using Google Vertex AI Gemini (model: {model_name})")
                return ChatVertexAI(
                    model=model_name,
                    project=os.getenv("GCP_PROJECT_ID"),
                    location=os.getenv("GOOGLE_VERTEX_LOCATION", "us-central1")
                )
            except ImportError:
                logger.warning("langchain-google-vertexai not installed, trying AI Studio...")
        
        # Fallback to AI Studio (API Key)
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = LLMConfig.API_KEYS[LLMProvider.GOOGLE]
            # If key is not in enviroment, check if user provided it differently or rely on library default
            if not api_key and not os.getenv("GOOGLE_API_KEY"):
                 raise ValueError("GOOGLE_API_KEY not set for AI Studio access")
            
            logger.info(f"Using Google AI Studio Gemini (model: {model_name})")
            return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
        except ImportError:
            raise ValueError("langchain-google-genai not installed. Install with: pip install langchain-google-genai")
    
    else:
        raise ValueError(f"Unsupported provider: {prov}")


def list_available_models() -> Dict[str, List[str]]:
    """List all available LLM models."""
    return LLMConfig.list_available_models()


def validate_llm_setup() -> Dict[str, Any]:
    """Validate LLM setup and configuration."""
    use_mock = os.getenv("LANGGRAPH_USE_MOCK_LLM", "false").lower() == "true"
    
    return {
        "use_mock_llm": use_mock,
        "api_keys_configured": LLMConfig.validate_api_keys(),
        "default_model": LLMConfig.get_default_model(),
        "available_models": list_available_models()
    }
