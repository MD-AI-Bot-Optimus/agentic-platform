#!/bin/bash
# Start both backend and frontend for Agentic Platform

# Start backend (FastAPI) on port 8002
cd "$(dirname "$0")"
PYTHONPATH=src uvicorn src.agentic_platform.api:app --reload --port 8003 --host 0.0.0.0 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend (Vite/React) on port 5173
cd ui
npm install
npm run dev

# When done, kill backend
kill $BACKEND_PID
