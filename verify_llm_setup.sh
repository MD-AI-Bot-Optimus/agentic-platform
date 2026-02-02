#!/bin/bash

# Quick LLM Verification Script
# Checks if API keys are configured and LLMs are accessible

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  LLM Configuration Verification                          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check .env file
if [ ! -f .env ]; then
    echo "✗ .env file not found"
    echo "  Run: cp .env.example .env"
    exit 1
fi

source .env

# Function to check API key
check_key() {
    local key_name=$1
    local key_value=${!key_name}
    
    if [ -z "$key_value" ]; then
        echo "✗ $key_name: NOT SET"
        return 1
    elif [ "$key_value" = "your-anthropic-api-key" ] || [ "$key_value" = "your-openai-api-key" ] || [ "$key_value" = "your-google-api-key" ]; then
        echo "⚠ $key_name: PLACEHOLDER (needs real key)"
        return 1
    else
        echo "✓ $key_name: CONFIGURED"
        return 0
    fi
}

echo "📋 Checking API Keys:"
echo ""

check_key "ANTHROPIC_API_KEY"
anthropic_ok=$?

check_key "OPENAI_API_KEY"
openai_ok=$?

if [ -f ./credentials.json ]; then
    echo "✓ GOOGLE_APPLICATION_CREDENTIALS: CONFIGURED (credentials.json)"
    google_ok=0
else
    echo "✗ GOOGLE_APPLICATION_CREDENTIALS: NOT FOUND (needs credentials.json)"
    google_ok=1
fi

echo ""
echo "📝 Configuration Summary:"
echo "  LLM_DEFAULT_MODEL: ${LLM_DEFAULT_MODEL:-not set}"
echo "  LANGGRAPH_USE_MOCK_LLM: ${LANGGRAPH_USE_MOCK_LLM:-false}"
echo ""

# Test endpoints if API is running
if command -v curl &> /dev/null; then
    echo "🧪 Testing API Endpoints:"
    echo ""
    
    # Check if server is running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ API Server: RUNNING"
        
        # List available models
        echo ""
        echo "Available Models:"
        curl -s http://localhost:8000/agent/models | python3 -m json.tool 2>/dev/null || echo "  (Could not parse response)"
        
    else
        echo "✗ API Server: NOT RUNNING"
        echo "  Start with: ./start_all.sh"
    fi
fi

echo ""
echo "🚀 Next Steps:"
if [ $anthropic_ok -eq 0 ]; then
    echo "  ✓ Claude 3.5 Sonnet is ready to use"
fi
if [ $openai_ok -eq 0 ]; then
    echo "  ✓ GPT-4 Turbo is ready to use"
fi
if [ $google_ok -eq 0 ]; then
    echo "  ✓ Gemini 1.5 Pro is ready to use"
fi

if [ $anthropic_ok -ne 0 ] && [ $openai_ok -ne 0 ] && [ $google_ok -ne 0 ]; then
    echo "  No LLM providers configured!"
    echo "  Run: ./setup_real_llms.sh"
fi

echo ""
echo "Test with:"
echo "  curl -X POST http://localhost:8000/agent/execute \\"
echo "    -F 'prompt=What is AI?' \\"
echo "    -F 'model=claude-3.5-sonnet'"
echo ""
