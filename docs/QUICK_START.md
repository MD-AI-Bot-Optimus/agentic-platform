# Quick Start Guide

## 🌐 Live Demo (Easiest)
Just visit: **https://agentic-platform-api-7erqohmwxa-uc.a.run.app/**

No setup needed. Try all three tabs:
- 📷 **OCR Demo** - Extract text from images
- ⚙️ **Run Workflow** - Execute YAML workflows
- 🔧 **MCP Tool Tester** - Call tools directly

## 💻 Local Development (5 minutes)

```bash
# Clone & install
git clone <repo-url> && cd agentic-platform
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ui && npm install && npm run dev &

# Backend (new terminal)
cd .. && python3 -m uvicorn src.agentic_platform.api:app --port 8003

# Open http://localhost:5173
```

## 🐳 Docker (One Command)

```bash
docker build -t agentic-platform .
docker run -p 8080:8080 agentic-platform
# Visit http://localhost:8080
```

## ☁️ Google Cloud Run

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete setup with auto-scaling and CI/CD.

## 📚 Next Steps

- **API Reference** → [api.md](api.md)
- **Architecture** → [architecture.md](architecture.md)
- **Workflow Examples** → [demo_workflow.yaml](../demo_workflow.yaml)
- **Contributing** → [CONTRIBUTING.md](CONTRIBUTING.md)
