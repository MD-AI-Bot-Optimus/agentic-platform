import os
import sys

# Ensure src is in path (up 2 levels from scripts/verification)
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from agentic_platform.integrations.factory import get_knowledge_base_provider

print("--- Testing Mock Provider (Default) ---")
# clear cache to ensure we get fresh provider
get_knowledge_base_provider.cache_clear()
if "KB_PROVIDER" in os.environ:
    del os.environ["KB_PROVIDER"]

mock_provider = get_knowledge_base_provider()
print(f"Provider: {mock_provider.__class__.__name__}")
result = mock_provider.search("neural network")
print(f"Result Preview: {result[:50]}...")
assert "Found 5 articles" in result, "Mock provider should return simple string matches"

print("\n--- Testing Enterprise Provider ---")
os.environ["KB_PROVIDER"] = "enterprise"
# clear cache to switch provider
get_knowledge_base_provider.cache_clear()

ent_provider = get_knowledge_base_provider()
print(f"Provider: {ent_provider.__class__.__name__}")
result = ent_provider.search("neural network")
print(f"Result Preview: {result[:100]}...")
assert "ENTERPRISE SEARCH RESULT" in result, "Enterprise provider should return structured report"

print("\n✅ Verification Successful: Application correctly switches providers based on configuration.")
