# Agentic Platform Demo UI

This is a minimal React UI for demoing the agentic-platform MVP.

## Features
- Upload workflow YAML and input JSON
- Select adapter (MCP or LangGraph)
- Run workflow and view results, tool results, and audit log

## Getting Started

1. Install dependencies:
   ```sh
   cd ui
   npm install
   ```
2. Start the development server:
   ```sh
   npm run dev
   ```
3. Ensure the FastAPI backend is running at http://localhost:8000
4. Open http://localhost:5173 in your browser

## Notes
- The UI proxies API requests to `/run-workflow/` to the backend.
- For production, build with `npm run build` and serve the static files.
