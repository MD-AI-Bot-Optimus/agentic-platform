import os
from functools import lru_cache
from .knowledge_base import KnowledgeBaseProvider, MockKnowledgeBase, EnterpriseKnowledgeBase
from .ocr import OCRProvider, MockOCR, GoogleCloudVisionOCR
from ..core.tenancy import TenantRegistry, get_current_tenant_id
from ..core.trace import add_trace_step

@lru_cache()
def get_knowledge_base_provider(tenant_id: str = None) -> KnowledgeBaseProvider:
    # If no tenant_id provided explicitly, resolve from context
    if tenant_id is None:
        tenant_id = get_current_tenant_id()
        
    config = TenantRegistry.get_config(tenant_id)
    provider_type = config.kb_provider
    
    print(f"[Factory] Resolving KB for tenant '{tenant_id}' -> {provider_type}")
    add_trace_step("Factory", f"Resolving KB Provider", f"Tenant: {tenant_id}, Type: {provider_type}")
    
    if provider_type == "enterprise":
        # Pass tenant-specific connection details here in a real app
        return EnterpriseKnowledgeBase(connection_string=f"mock://{tenant_id}-vector-db")
    else:
        return MockKnowledgeBase()

@lru_cache()
def get_ocr_provider(tenant_id: str = None, credentials_json: str = None) -> OCRProvider:
    if tenant_id is None:
        tenant_id = get_current_tenant_id()

    config = TenantRegistry.get_config(tenant_id)
    provider_type = config.ocr_provider

    print(f"[Factory] Resolving OCR for tenant '{tenant_id}' -> {provider_type}")
    add_trace_step("Factory", f"Resolving OCR Provider", f"Tenant: {tenant_id}, Type: {provider_type}")
    
    if provider_type == "mock":
        return MockOCR()
    else:
        # Enterprise usage
        return GoogleCloudVisionOCR(credentials_json)
