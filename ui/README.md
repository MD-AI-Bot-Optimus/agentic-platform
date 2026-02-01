# Agentic Platform Demo UI

Modern React dashboard for the agentic-platform, built with Material-UI and Vite.

## Features

### OCR Demo
- Upload images (JPEG, PNG, etc.)
- Extract text using Google Cloud Vision API
- View formatted text output with confidence scores
- Test with sample images: `handwriting.jpg`, `letter.jpg`, etc.

### MCP Tool Tester
- Discover available MCP tools via `/mcp/tools` endpoint
- Select any registered tool
- Input tool arguments as JSON
- View JSON-RPC 2.0 responses in real-time
- Built-in error handling and display

### Workflow Runner
- Upload workflow YAML definitions
- Upload input JSON artifacts
- Select adapter (MCP or LangGraph)
- Execute workflows and view:
  - Workflow results
  - Tool results from each step
  - Complete audit log with timestamps

## UI Design

### Layout
- **2-Column Responsive Grid** - OCR, MCP, and Workflow boxes side-by-side on desktop
- **Sticky Header** - "Agentic Platform Demo UI" title stays visible while scrolling
- **Highway 1 Background** - Pacific Coast imagery for visual appeal
- **Material-UI Components** - Cards, buttons, text fields, selects

### Responsiveness
- Boxes stack to 1 column on mobile/tablet
- Full-width layout preserved on smaller screens
- Automatic responsive breakpoints via Material-UI Grid

## Getting Started

### Prerequisites
- Node.js 18+
- Backend API running at http://localhost:8002

### Installation

```sh
cd ui
npm install
```

### Development

Start the Vite dev server:
```sh
npm run dev
```

The UI will be available at http://localhost:5173

Hot module reloading is enabled—changes to React components reload instantly.

### Production Build

```sh
npm run build
```

Output files go to `ui/dist/`. Serve with any static host:
```sh
npm run preview
```

## Backend Integration

The UI connects to the FastAPI backend at http://localhost:8002:

- **POST** `/run-ocr/` - Upload image for OCR
- **GET** `/mcp/tools` - List available MCP tools
- **POST** `/mcp/request` - Call MCP tool with JSON-RPC
- **POST** `/run-workflow/` - Execute workflow YAML

### API Proxy

For local development, Vite proxies API requests. In production, ensure CORS is configured or use a reverse proxy.

## Components

### App.jsx
Main React component with:
- OCR demo form and results
- MCP tool selector and caller
- Workflow file uploader and executor
- Material-UI Grid layout

### index.html
Entry point with:
- Responsive meta tags
- Material-UI theme setup
- Root div for React mounting

## Testing

Run tests with:
```sh
npm test
```

## Technologies

- **React** 18.3.1 - UI framework
- **Material-UI** 7.3.7 - Component library
- **Vite** 4.5.14 - Build tool and dev server
- **Axios** (via fetch) - HTTP client

## Troubleshooting

### Port Already in Use
If port 5173 is busy, Vite will try 5174, 5175, etc.

### Backend Not Responding
Ensure FastAPI is running:
```sh
PYTHONPATH=src uvicorn src.agentic_platform.api:app --reload --port 8002
```

### CORS Issues
Check backend CORS configuration in `src/agentic_platform/api.py`

## Next Steps

1. Add workflow visualization (DAG diagram)
2. Add result export (JSON, CSV)
3. Add workflow history and replay
4. Add user authentication
5. Add dark mode theme

## Contributing

Follow the existing component structure and Material-UI patterns. All new features should include tests.
