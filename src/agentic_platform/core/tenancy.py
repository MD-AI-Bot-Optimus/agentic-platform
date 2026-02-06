from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Global context variable to hold the current tenant ID
# This allows us to access the tenant context anywhere in the async call stack
_current_tenant: ContextVar[Optional[str]] = ContextVar("current_tenant", default="default")

@dataclass
class TenantConfig:
    """Configuration for a specific tenant."""
    tenant_id: str
    name: str
    tier: str  # e.g., 'free', 'pro', 'enterprise'
    kb_provider: str  # 'mock' or 'enterprise'
    ocr_provider: str  # 'mock', 'google'
    features: Dict[str, Any]

class TenantRegistry:
    """
    Simulated registry of tenants.
    In a real system, this would fetch from a database or configuration service.
    """
    _tenants = {
        "default": TenantConfig(
            tenant_id="default",
            name="Default Mock User",
            tier="free",
            kb_provider="mock",
            ocr_provider="mock",
            features={"max_requests": 100}
        ),
        "startup_inc": TenantConfig(
            tenant_id="startup_inc",
            name="Startup Inc.",
            tier="pro",
            kb_provider="mock",
            ocr_provider="mock",
            features={"max_requests": 1000}
        ),
        "enterprise_corp": TenantConfig(
            tenant_id="enterprise_corp",
            name="Global Enterprise Corp",
            tier="enterprise",
            kb_provider="enterprise",
            ocr_provider="google",
            features={"max_requests": 10000, "compliance_logging": True}
        )
    }

    @classmethod
    def get_config(cls, tenant_id: str) -> TenantConfig:
        config = cls._tenants.get(tenant_id)
        if not config:
            # Fallback to default for unknown tenants in this mock
            print(f"⚠️ Warning: Unknown tenant '{tenant_id}', using default config.")
            return cls._tenants["default"]
        return config

def get_current_tenant_id() -> str:
    """Get the tenant ID from the current context."""
    return _current_tenant.get() or "default"

def set_current_tenant_id(tenant_id: str):
    """Set the tenant ID for the current context."""
    return _current_tenant.set(tenant_id)
