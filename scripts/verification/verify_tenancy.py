import os
import sys

# Ensure src is in path (up 2 levels from scripts/verification)
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from agentic_platform.core.tenancy import set_current_tenant_id, get_current_tenant_id
from agentic_platform.integrations.factory import get_knowledge_base_provider, get_ocr_provider

def verify_tenant(tenant_id: str, expected_kb_type: str, expected_ocr_type: str):
    print(f"\n--- Switching to Tenant: {tenant_id} ---")
    token = set_current_tenant_id(tenant_id)
    
    try:
        current = get_current_tenant_id()
        assert current == tenant_id, f"Context did not stick! Got {current}"
        
        # Clear lru_cache to ensure we resolve fresh
        get_knowledge_base_provider.cache_clear()
        get_ocr_provider.cache_clear()

        # Resolve Providers
        kb = get_knowledge_base_provider()
        ocr = get_ocr_provider()
        
        kb_name = kb.__class__.__name__
        ocr_name = ocr.__class__.__name__
        
        print(f"KB Provider:  {kb_name}")
        print(f"OCR Provider: {ocr_name}")
        
        if expected_kb_type not in kb_name:
            print(f"❌ FAIL: Expected KB {expected_kb_type}, got {kb_name}")
            return False
            
        if expected_ocr_type not in ocr_name:
            print(f"❌ FAIL: Expected OCR {expected_ocr_type}, got {ocr_name}")
            return False

        # If it's the Enterprise tenant, verify the connection string simulation
        if tenant_id == "enterprise_corp" and hasattr(kb, "connection_string"):
            print(f"Connection:   {kb.connection_string}")
            assert "enterprise_corp" in kb.connection_string, "Connection string missing tenant ID!"

        return True

    finally:
        set_current_tenant_id(token.old_value if hasattr(token, 'old_value') else "default")

if __name__ == "__main__":
    t1 = verify_tenant("startup_inc", "MockKnowledgeBase", "MockOCR")
    t2 = verify_tenant("enterprise_corp", "EnterpriseKnowledgeBase", "GoogleCloudVisionOCR")
    
    if t1 and t2:
        print("\n✅ Verification Successful: Multi-Tenancy Context Switching Operational.")
        exit(0)
    else:
        print("\n❌ Verification Failed.")
        exit(1)
