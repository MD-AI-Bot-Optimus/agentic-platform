# Real LLM Setup Guide

Complete guide to wire real LLMs (Claude, GPT-4, Gemini) to the Agentic Platform.

## Quick Start (3 minutes)

```bash
# 1. Run setup script
./setup_real_llms.sh

# 2. Restart API server
./start_all.sh

# 3. Visit demo page
open http://localhost:8000/agent_demo.html
```

## Detailed Setup by Provider

### Option 1: Claude 3.5 Sonnet (Anthropic) ⭐ Recommended

**Why Claude:**
- ✅ Best reasoning and accuracy
- ✅ Fast responses
- ✅ Excellent for complex tasks
- ✅ ~$3 per 1M input tokens

**Setup Steps:**

1. **Get API Key:**
   ```
   Visit: https://console.anthropic.com/account/keys
   Click: "Create Key"
   Copy: Key value
   ```

2. **Add to .env:**
   ```bash
   # In .env file
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
   LLM_DEFAULT_MODEL=claude-3.5-sonnet
   ```

3. **Verify:**
   ```bash
   ./verify_llm_setup.sh
   ```

4. **Test:**
   ```bash
   curl -X POST http://localhost:8000/agent/execute \
     -F 'prompt=Explain quantum computing in simple terms' \
     -F 'model=claude-3.5-sonnet'
   ```

**Available Claude Models:**
- `claude-3.5-sonnet` - Latest, best reasoning (recommended)
- `claude-3-opus` - Most powerful, slower
- `claude-3-sonnet` - Good balance
- `claude-3-haiku` - Fast, good for simple tasks

---

### Option 2: GPT-4 Turbo (OpenAI)

**Why GPT-4:**
- ✅ Very capable model
- ✅ Good for most tasks
- ✅ ~$0.01 per 1K input tokens (turbo)
- ✅ Large context window

**Setup Steps:**

1. **Get API Key:**
   ```
   Visit: https://platform.openai.com/account/api-keys
   Click: "Create new secret key"
   Copy: Key value
   ```

2. **Add to .env:**
   ```bash
   # In .env file
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
   LLM_DEFAULT_MODEL=gpt-4-turbo
   ```

3. **Verify:**
   ```bash
   ./verify_llm_setup.sh
   ```

4. **Test:**
   ```bash
   curl -X POST http://localhost:8000/agent/execute \
     -F 'prompt=Explain quantum computing in simple terms' \
     -F 'model=gpt-4-turbo'
   ```

**Available OpenAI Models:**
- `gpt-4-turbo` - Latest, best performance
- `gpt-4` - Original GPT-4
- `gpt-3.5-turbo` - Fast, cheaper

---

### Option 3: Gemini 1.5 Pro (Google Vertex AI)

**Why Gemini:**
- ✅ Strong reasoning
- ✅ Excellent for multimodal tasks
- ✅ ~$1.25 per 1M input tokens
- ✅ Long context window

**Setup Steps:**

1. **Create Service Account:**
   ```
   Visit: https://console.cloud.google.com/iam-admin/serviceaccounts
   Click: "Create Service Account"
   Fill: Name = "agentic-platform-llm"
   Click: "Create and Continue"
   ```

2. **Create JSON Key:**
   ```
   Click: "Keys" tab
   Click: "Add Key" → "Create new key"
   Select: "JSON"
   Click: "Create"
   Save: credentials.json to project root
   ```

3. **Enable Vertex AI API:**
   ```
   Visit: https://console.cloud.google.com/apis/library
   Search: "Vertex AI API"
   Click: "Enable"
   ```

4. **Add to .env:**
   ```bash
   # In .env file
   GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
   GCP_PROJECT_ID=your-project-id
   LLM_DEFAULT_MODEL=gemini-1.5-pro
   ```

5. **Verify:**
   ```bash
   ./verify_llm_setup.sh
   ```

6. **Test:**
   ```bash
   curl -X POST http://localhost:8000/agent/execute \
     -F 'prompt=Explain quantum computing in simple terms' \
     -F 'model=gemini-1.5-pro'
   ```

**Available Gemini Models:**
- `gemini-1.5-pro` - Most capable, good for complex tasks
- `gemini-1.5-flash` - Faster, more cost-effective
- `gemini-2` - Latest (when available)

---

## Testing Your Setup

### Method 1: Verification Script
```bash
./verify_llm_setup.sh
```

Checks:
- ✓ .env file exists
- ✓ API keys are set
- ✓ API server is running
- ✓ Models are available

### Method 2: Web Interface
```bash
# Restart server
./start_all.sh

# Visit demo page
open http://localhost:8000/agent_demo.html

# Select LLM from dropdown
# Enter prompt
# Click "Execute Agent"
```

### Method 3: API Endpoint
```bash
# List available models
curl http://localhost:8000/agent/models | json_pp

# Execute agent with specific model
curl -X POST http://localhost:8000/agent/execute \
  -F 'prompt=What is the capital of France?' \
  -F 'model=claude-3.5-sonnet'
```

### Method 4: Python
```python
from agentic_platform.llm import get_llm_model
from agentic_platform.adapters.langgraph_agent import LangGraphAgent

# Get Claude
llm = get_llm_model(model="claude-3.5-sonnet")

# Create agent
agent = LangGraphAgent(model="claude-3.5-sonnet", llm=llm)

# Execute
result = agent.execute("What is AI?")
print(result.final_output)
```

---

## Common Issues & Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

**Solution:**
```bash
# 1. Check .env file
cat .env | grep ANTHROPIC

# 2. Ensure key is real (not placeholder)
# Should NOT be: your-anthropic-api-key
# Should be: sk-ant-xxxxxxxxxxxxx

# 3. Restart API server
./start_all.sh
```

### Issue: "API key invalid" or "Unauthorized"

**Solution:**
```bash
# 1. Verify key is correct
# Copy from provider console again

# 2. Check for extra spaces
# In .env: ANTHROPIC_API_KEY=sk-ant-xxx (no spaces around =)

# 3. Test with provider's own API first
python3 -c "
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model='claude-3.5-sonnet', api_key='YOUR_KEY_HERE')
print(llm.invoke('hi'))
"
```

### Issue: "Model not found"

**Solution:**
```bash
# 1. Check available models
curl http://localhost:8000/agent/models

# 2. Use correct model name:
# Claude: claude-3.5-sonnet, claude-3-opus, etc.
# GPT-4: gpt-4-turbo, gpt-4, gpt-3.5-turbo
# Gemini: gemini-1.5-pro, gemini-1.5-flash, gemini-2
```

### Issue: API Server shows "ImportError"

**Solution:**
```bash
# 1. Install required package
pip install langchain-anthropic  # for Claude
pip install langchain-openai     # for GPT-4
pip install langchain-google-vertexai  # for Gemini

# 2. Or reinstall all
pip install -r pyproject.toml

# 3. Restart server
./start_all.sh
```

### Issue: Mock LLM is being used instead of real LLM

**Solution:**
```bash
# 1. Check .env
cat .env | grep LANGGRAPH_USE_MOCK

# 2. Set to false
LANGGRAPH_USE_MOCK_LLM=false

# 3. Restart server
./start_all.sh
```

---

## Pricing Comparison

| Provider | Model | Cost | Speed | Best For |
|----------|-------|------|-------|----------|
| Anthropic | Claude 3.5 Sonnet | $3/1M tokens | Fast | Reasoning, Accuracy |
| OpenAI | GPT-4 Turbo | $10/1M tokens | Medium | General tasks |
| Google | Gemini 1.5 Pro | $1.25/1M tokens | Very Fast | Efficiency |
| Local | Mock LLM | Free | Instant | Testing |

**Example Costs:**
- 1000 requests × 100 tokens = 100K tokens
- Claude: $0.30 / month
- GPT-4: $1.00 / month  
- Gemini: $0.125 / month
- Mock: $0 / month

---

## Advanced Configuration

### Use Different Model by Default
```bash
# In .env
LLM_DEFAULT_MODEL=gpt-4-turbo
```

Then requests without model parameter will use GPT-4 Turbo:
```bash
curl -X POST http://localhost:8000/agent/execute \
  -F 'prompt=Hello'
# Uses GPT-4 Turbo by default
```

### Environment Variable Reference
```bash
# Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# GPT-4 (OpenAI)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Gemini (Google)
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_VERTEX_LOCATION=us-central1

# Default model
LLM_DEFAULT_MODEL=claude-3.5-sonnet

# Use mock for testing
LANGGRAPH_USE_MOCK_LLM=true  # or false for real LLMs
```

### Fallback to Mock LLM
If an API key is not configured, the system automatically falls back to mock LLM:
```python
# If ANTHROPIC_API_KEY is not set:
llm = get_llm_model(model="claude-3.5-sonnet")
# Returns MockLLM instead, no error
```

---

## Next Steps

1. ✅ Set up one LLM provider (follow guide above)
2. ✅ Run verification: `./verify_llm_setup.sh`
3. ✅ Test in web UI: http://localhost:8000/agent_demo.html
4. ✅ Try curl commands above
5. ✅ Integrate with workflows (see workflow docs)

---

## Support

**Check logs:**
```bash
# View API logs
tail -f logs/api.log

# View agent execution logs
tail -f logs/agent.log
```

**Test API directly:**
```bash
# List models and status
curl -v http://localhost:8000/agent/models

# Execute with verbosity
curl -v -X POST http://localhost:8000/agent/execute \
  -F 'prompt=test' \
  -F 'model=claude-3.5-sonnet'
```

**Python debugging:**
```python
from agentic_platform.llm import validate_llm_setup
status = validate_llm_setup()
print(status)
# Output shows which providers are ready
```
