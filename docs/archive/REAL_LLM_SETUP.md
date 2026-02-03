# Real LLM Wiring - Quick Reference

Everything is set up and ready to go! Here's what was changed:

## 🎯 What Was Done

### 1. **API Endpoint Enhanced**
- ✅ `/agent/execute` now supports real LLMs (Claude, GPT-4, Gemini)
- ✅ Auto-fallback to mock LLM if API key not configured
- ✅ Returns model_used and llm_setup info in response

### 2. **New Endpoint Added**
- ✅ `/agent/models` - Lists available models and API key status

### 3. **Scripts Created**
- ✅ `setup_real_llms.sh` - Interactive setup wizard
- ✅ `verify_llm_setup.sh` - Verification checker

### 4. **Documentation**
- ✅ `docs/LLM_SETUP.md` - Comprehensive setup guide with troubleshooting

## ⚡ Quick Start (3 minutes)

### Option A: Interactive Setup
```bash
./setup_real_llms.sh
```
Then follow the prompts to add your API key.

### Option B: Manual Setup

**For Claude 3.5 Sonnet:**
```bash
# 1. Get key from https://console.anthropic.com/account/keys
# 2. Edit .env and add:
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
LLM_DEFAULT_MODEL=claude-3.5-sonnet

# 3. Restart server
pkill -f uvicorn
PYTHONPATH=./src ./.venv/bin/python -m uvicorn agentic_platform.api:app --port 8000 &
```

**For GPT-4 Turbo:**
```bash
# 1. Get key from https://platform.openai.com/account/api-keys
# 2. Edit .env and add:
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
LLM_DEFAULT_MODEL=gpt-4-turbo
```

**For Gemini 1.5 Pro:**
```bash
# 1. Follow Google Vertex AI setup in docs/LLM_SETUP.md
# 2. Download credentials.json
# 3. Copy to project root
```

## 🧪 Verification

```bash
# Check setup status
./verify_llm_setup.sh

# Test API
curl http://localhost:8000/agent/models | json_pp

# Test agent with specific model
curl -X POST http://localhost:8000/agent/execute \
  -F 'prompt=What is AI?' \
  -F 'model=claude-3.5-sonnet'
```

## 🌐 Web UI

Visit the demo page to test:
```
http://localhost:8000/agent_demo.html
```

Select your LLM from the dropdown and submit a prompt.

## 📁 Files Changed

- [src/agentic_platform/api.py](src/agentic_platform/api.py) - Updated `/agent/execute`, added `/agent/models`
- [src/agentic_platform/llm/__init__.py](src/agentic_platform/llm/__init__.py) - Already had LLM factory (no changes)
- [.env.example](.env.example) - Already had config template (no changes)
- [setup_real_llms.sh](setup_real_llms.sh) - NEW interactive setup script
- [verify_llm_setup.sh](verify_llm_setup.sh) - NEW verification script
- [docs/LLM_SETUP.md](docs/LLM_SETUP.md) - NEW comprehensive guide

## 🔑 Supported Models

| Provider | Models | Cost | Speed |
|----------|--------|------|-------|
| **Anthropic** | claude-3.5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku | $3/1M tokens | Fast ⚡ |
| **OpenAI** | gpt-4-turbo, gpt-4, gpt-3.5-turbo | $10/1M tokens | Medium |
| **Google** | gemini-1.5-pro, gemini-1.5-flash, gemini-2 | $1.25/1M tokens | Very Fast ⚡⚡ |
| **Local** | mock-llm | Free | Instant |

## 🚀 Next Steps

1. **Try one provider** (Claude recommended for best reasoning)
2. **Restart server** after adding API key
3. **Test in Web UI** or with curl
4. **(Optional) Add more providers** as needed

## ❓ Troubleshooting

**"API key not set" warnings?**
→ Normal if provider not configured. System falls back to mock LLM.

**"Module not found" error?**
→ Run: `./.venv/bin/pip install [package-name]`

**Agent still using mock when I added key?**
→ Restart the server: `pkill -f uvicorn && (restart command)`

**Want detailed troubleshooting?**
→ See `docs/LLM_SETUP.md` section "Common Issues & Troubleshooting"

## 📊 Current Status

```
✅ API Server: Running
✅ Mock LLM: Ready (free testing)
✅ Claude Support: Ready (needs API key)
✅ GPT-4 Support: Ready (needs API key)
✅ Gemini Support: Ready (needs credentials)
✅ Web UI: Ready
✅ Fallback Logic: Working
```

## 🎓 How It Works

1. **Request comes to `/agent/execute`** with model parameter
2. **LLM factory checks** for API key in environment
3. **If key found**: Uses real LLM (Claude/GPT-4/Gemini)
4. **If key not found**: Falls back to mock LLM silently
5. **Agent executes** and returns reasoning, output, tools
6. **Response includes** model_used and llm_setup status

## 💡 Pro Tips

- Use `mock-llm` for testing and development (0 cost)
- Switch between models by changing .env and restarting
- Set `LLM_DEFAULT_MODEL` to your preferred model
- Check `llm_setup` in API response to see which providers are ready

---

**Questions?** See [docs/LLM_SETUP.md](docs/LLM_SETUP.md) for comprehensive guide.

**Ready to try real LLMs?** Run `./setup_real_llms.sh` now! 🚀
