#!/bin/bash

# Setup Real LLMs for Agentic Platform
# This script helps configure API keys for Claude, GPT-4, or Gemini

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Agentic Platform - Real LLM Setup                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "✓ .env file exists"
    source .env
else
    echo "→ Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env created (edit with your API keys)"
fi

echo ""
echo "Which LLM provider would you like to configure?"
echo "1) Claude 3.5 Sonnet (Anthropic)"
echo "2) GPT-4 Turbo (OpenAI)"
echo "3) Gemini 1.5 Pro (Google)"
echo "4) All of the above"
echo "0) Skip configuration"
echo ""
read -p "Enter your choice (0-4): " choice

setup_anthropic() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  Claude 3.5 Sonnet Setup (Anthropic)                      ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Get your API key:"
    echo "1. Go to https://console.anthropic.com/account/keys"
    echo "2. Create new API key"
    echo "3. Copy the key"
    echo ""
    read -sp "Paste your ANTHROPIC_API_KEY: " api_key
    echo ""
    
    if [ -n "$api_key" ]; then
        # Update or add to .env
        if grep -q "ANTHROPIC_API_KEY=" .env; then
            sed -i '' "s|ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=$api_key|" .env
        else
            echo "ANTHROPIC_API_KEY=$api_key" >> .env
        fi
        echo "✓ Anthropic API key saved"
        
        # Test the key
        test_anthropic "$api_key"
    else
        echo "✗ Skipped Anthropic setup"
    fi
}

setup_openai() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  GPT-4 Turbo Setup (OpenAI)                               ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Get your API key:"
    echo "1. Go to https://platform.openai.com/account/api-keys"
    echo "2. Create new secret key"
    echo "3. Copy the key"
    echo ""
    read -sp "Paste your OPENAI_API_KEY: " api_key
    echo ""
    
    if [ -n "$api_key" ]; then
        if grep -q "OPENAI_API_KEY=" .env; then
            sed -i '' "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$api_key|" .env
        else
            echo "OPENAI_API_KEY=$api_key" >> .env
        fi
        echo "✓ OpenAI API key saved"
        
        # Test the key
        test_openai "$api_key"
    else
        echo "✗ Skipped OpenAI setup"
    fi
}

setup_google() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  Gemini 1.5 Pro Setup (Google Vertex AI)                  ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Get your credentials:"
    echo "1. Go to https://console.cloud.google.com/vertex-ai"
    echo "2. Create service account (or use existing)"
    echo "3. Download JSON key"
    echo "4. Save as credentials.json in project root"
    echo ""
    read -p "Path to credentials.json: " cred_path
    
    if [ -f "$cred_path" ]; then
        cp "$cred_path" ./credentials.json
        
        # Extract project ID from credentials
        project_id=$(grep -o '"project_id": "[^"]*' ./credentials.json | cut -d'"' -f4)
        
        if grep -q "GOOGLE_APPLICATION_CREDENTIALS=" .env; then
            sed -i '' 's|GOOGLE_APPLICATION_CREDENTIALS=.*|GOOGLE_APPLICATION_CREDENTIALS=./credentials.json|' .env
        else
            echo "GOOGLE_APPLICATION_CREDENTIALS=./credentials.json" >> .env
        fi
        
        if [ -n "$project_id" ]; then
            if grep -q "GCP_PROJECT_ID=" .env; then
                sed -i '' "s|GCP_PROJECT_ID=.*|GCP_PROJECT_ID=$project_id|" .env
            else
                echo "GCP_PROJECT_ID=$project_id" >> .env
            fi
            echo "✓ Google credentials saved (project: $project_id)"
            test_google
        else
            echo "✗ Could not extract project ID from credentials"
        fi
    else
        echo "✗ Credentials file not found: $cred_path"
    fi
}

test_anthropic() {
    local key=$1
    echo ""
    echo "Testing Anthropic connection..."
    python3 << EOF
import os
os.environ["ANTHROPIC_API_KEY"] = "$key"
try:
    from langchain_anthropic import ChatAnthropic
    llm = ChatAnthropic(model="claude-3.5-sonnet", api_key="$key")
    response = llm.invoke("Say 'Hello' and nothing else")
    print(f"✓ Connection successful! Response: {response.content[:50]}...")
except Exception as e:
    print(f"✗ Connection failed: {str(e)}")
EOF
}

test_openai() {
    local key=$1
    echo ""
    echo "Testing OpenAI connection..."
    python3 << EOF
import os
os.environ["OPENAI_API_KEY"] = "$key"
try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4-turbo", api_key="$key")
    response = llm.invoke("Say 'Hello' and nothing else")
    print(f"✓ Connection successful! Response: {response.content[:50]}...")
except Exception as e:
    print(f"✗ Connection failed: {str(e)}")
EOF
}

test_google() {
    echo ""
    echo "Testing Google Vertex AI connection..."
    python3 << EOF
import os
try:
    from langchain_google_vertexai import ChatVertexAI
    llm = ChatVertexAI(model="gemini-1.5-pro")
    response = llm.invoke("Say 'Hello' and nothing else")
    print(f"✓ Connection successful! Response: {response.content[:50]}...")
except Exception as e:
    print(f"✗ Connection failed: {str(e)}")
EOF
}

# Handle user choice
case $choice in
    1) setup_anthropic ;;
    2) setup_openai ;;
    3) setup_google ;;
    4) 
        setup_anthropic
        setup_openai
        setup_google
        ;;
    0) echo "Skipped LLM setup"; exit 0 ;;
    *) echo "Invalid choice"; exit 1 ;;
esac

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Setup Complete!                                          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Restart the API server:"
echo "   ./start_all.sh"
echo ""
echo "2. Test the agent with real LLM:"
echo "   Visit: http://localhost:8000/agent_demo.html"
echo "   Select your LLM from the dropdown"
echo ""
echo "3. Or use curl:"
echo "   curl -X POST http://localhost:8000/agent/execute \\"
echo "     -F 'prompt=What is AI?' \\"
echo "     -F 'model=claude-3.5-sonnet'"
echo ""
