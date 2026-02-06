import React, { useState } from 'react';
import { Container, Typography, Button, Card, CardContent, Box, Alert, CircularProgress, FormControl, InputLabel, Select, MenuItem, TextField, Grid, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material';
import MermaidDiagram from './components/MermaidDiagram';

// Architecture Diagrams
const AGENT_PROMPTS = [
  "What is the capital of France?",
  "Research the history of AI agents.",
  "Write a Python script to calculate Fibonacci numbers.",
  "Explain the difference between TCP and UDP.",
  "Who is the CEO of Google?"
];

const WORKFLOW_EXAMPLES = {
  simple: `name: Simple Linear Flow
steps:
  - id: step1
    function: process_data
    inputs: 
      data: context.input
  - id: final
    function: generate_summary
    inputs:
      text: step1.output
`,
  parallel: `name: Parallel Processing
steps:
  - id: start
    function: split_data
    inputs: 
      data: context.input
  - id: branch_a
    function: process_chunk_a
    inputs:
      chunk: start.output.chunk_a
  - id: branch_b
    function: process_chunk_b
    inputs:
      chunk: start.output.chunk_b
  - id: merge
    function: merge_results
    inputs:
      res_a: branch_a.output
      res_b: branch_b.output
`
};

const DIAGRAMS = {
  ocr: `graph LR
    %% Styles
    classDef blue fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b
    classDef green fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32
    classDef orange fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#ef6c00
    classDef user fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#7b1fa2

    User((User)):::user -->|Uploads Image| Frontend[React UI]:::blue
    Frontend -->|POST /run-ocr| API[FastAPI Backend]:::green
    API -->|Instantiates| Wrapper[GoogleVisionOCR Tool]:::green
    Wrapper -->|Sends Bytes| Cloud[Google Cloud Vision]:::orange
    Cloud -->|Returns JSON| Wrapper
    Wrapper -->|Parses Text| API
    API -->|Returns Result| Frontend`,

  mcp: `sequenceDiagram
    participant UI as Frontend (React)
    participant TR as ToolRegistry (Python)
    participant Tool as Tool Function
    
    rect rgb(240, 248, 255)
    Note over UI,TR: JSON-RPC 2.0 Request
    UI->>TR: POST /mcp/request
    end
    
    TR->>TR: Validate Method & Params
    
    rect rgb(255, 250, 240)
    Note over TR,Tool: Execution
    TR->>Tool: Call Implementation
    Tool-->>TR: Return Data
    end
    
    TR-->>UI: { "result": { "content": [...] } }`,

  workflow: `stateDiagram-v2
    classDef start fill:#e1f5fe,stroke:#01579b,font-weight:bold
    classDef process fill:#e8f5e9,stroke:#2e7d32
    classDef endNode fill:#ffebee,stroke:#c62828

    [*] --> Start:::start
    Start --> ParseYAML:::process
    ParseYAML --> CompileGraph:::process
    CompileGraph --> ExecuteStep1:::process
    ExecuteStep1 --> ExecuteStep2:::process
    ExecuteStep2 --> FinalOutput:::endNode
    FinalOutput --> [*]`,

  agent: `graph TD
    classDef agent fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef llm fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef tool fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef router fill:#fff9c4,stroke:#fbc02d,stroke-width:2px

    User(User Prompt) -->|Input| Agent[ReAct Loop]:::agent
    Agent -->|Context| LLM{Gemini 2.0}:::llm
    LLM -->|Thought| Router{Action?}:::router
    Router -->|Call Tool| Tool[Execute Tool]:::tool
    Router -->|Answer| Final[Final Response]:::agent
    Tool -->|Observation| Agent
    Final -->|Output| User`
};
import pacificBg from './assets/pacific_bg.png';

// Modern art background styles with pacific image from past
const modernArtStyle = {
  backgroundImage: `url(${pacificBg})`,
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  backgroundAttachment: 'fixed',
  minHeight: '100vh',
  width: '100%',
  position: 'relative',
  transition: 'all 0.5s ease',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.4)', // Increased transparency for better visibility
    backdropFilter: 'blur(12px)',
    zIndex: 0,
  }
};

// Add global styles for background and animations
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes floatIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
  }
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  body, html {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
    background-image: url(${pacificBg}) !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    min-height: 100vh;
  }
  #root {
    position: relative;
    z-index: 1;
    min-height: 100vh;
    background: transparent !important;
  }
  .MuiContainer-root {
    background: transparent !important;
  }
`;
document.head.appendChild(styleSheet);

// API Base URL - Use empty string to use Vite proxy in dev, otherwise use production URL
const API_BASE_URL = (typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) || (
  typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? '' // Use Vite proxy
    : 'https://agentic-platform-api-170705020917.us-central1.run.app'
);

// Default MCP tools list (fallback when API is unavailable)
const defaultMcpTools = [
  {
    name: 'google_vision_ocr',
    description: 'Extract text from images using Google Cloud Vision API',
    inputSchema: {
      type: 'object',
      properties: {
        image_path: { type: 'string', description: 'Path to the image file to OCR.' },
        credentials_json: { type: 'string', description: 'Path to Google credentials JSON file.' }
      },
      required: ['image_path']
    }
  }
];


// Educational Banner Component
const LearningBanner = ({ title, description, codeRef, concept, icon }) => (
  <Box sx={{
    background: 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)',
    borderRadius: 2,
    p: 2,
    mb: 3,
    border: '1px solid #bbdefb',
    boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
  }}>
    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
      <Typography sx={{ fontSize: '2rem' }}>{icon}</Typography>
      <Box>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1565c0', display: 'flex', alignItems: 'center', gap: 1 }}>
          🎓 How this works: <span style={{ background: '#fff', padding: '2px 8px', borderRadius: '4px', border: '1px solid #90caf9', fontSize: '0.8rem', color: '#1976d2' }}>{concept}</span>
        </Typography>
        <Typography variant="body2" sx={{ mt: 1, color: '#0d47a1', lineHeight: 1.6 }}>
          {description}
        </Typography>
        {codeRef && (
          <Box sx={{ mt: 1.5, display: 'flex', gap: 1, alignItems: 'center' }}>
            <Typography variant="caption" sx={{ fontWeight: 600, color: '#555' }}>Code Reference:</Typography>
            <code style={{ background: 'rgba(255,255,255,0.7)', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem', fontFamily: 'monospace', border: '1px solid #ddd' }}>
              {codeRef}
            </code>
          </Box>
        )}
      </Box>
    </Box>
  </Box>
);



function App() {
  const [activeView, setActiveView] = useState('ocr');
  // ... existing state ...
  // (We need to keep the state definitions, so I will target specific insertion points below instead of replacing the whole App)
  // But since I cannot do multiple disjoint edits easily in one go without 'multi_replace', 
  // and I don't see 'multi_replace' in my allowed tools (wait, I do check: yes, I have multi_replace_file_content).
  // I will use multi_replace_file_content for this.


  // Workflow state
  const [workflowFile, setWorkflowFile] = useState(null);
  const [inputFile, setInputFile] = useState(null);
  const [adapter, setAdapter] = useState('mcp');

  // Architecture Modal State
  const [archModalOpen, setArchModalOpen] = useState(false);
  const [currentDiagram, setCurrentDiagram] = useState(null);

  const handleOpenArch = (type) => {
    setCurrentDiagram(DIAGRAMS[type]);
    setArchModalOpen(true);
  };

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);


  // OCR demo state
  const [ocrImage, setOcrImage] = useState(null);
  const [ocrResult, setOcrResult] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrError, setOcrError] = useState(null);
  const [qualityResult, setQualityResult] = useState(null);
  const [qualityLoading, setQualityLoading] = useState(false);

  // MCP demo state
  const [mcpToolName, setMcpToolName] = useState('google_vision_ocr');
  const [mcpArgs, setMcpArgs] = useState('{"image_path": "sample_data/letter.jpg"}');
  const [mcpResult, setMcpResult] = useState(null);
  const [mcpAvailableTools, setMcpAvailableTools] = useState([]);
  const [mcpLoading, setMcpLoading] = useState(false);
  const [mcpError, setMcpError] = useState(null);

  // LangGraph Agent state
  const [agentPrompt, setAgentPrompt] = useState('What is artificial intelligence?');
  const [agentModel, setAgentModel] = useState('mock-llm');
  const [agentMaxIterations, setAgentMaxIterations] = useState(10);
  const [agentResult, setAgentResult] = useState(null);
  const [agentLoading, setAgentLoading] = useState(false);
  const [agentError, setAgentError] = useState(null);
  const [expandedStep, setExpandedStep] = useState(null);

  /* RE-APPLIED FIX: Dedicated Backend Fetch Process */
  const [previewUrl, setPreviewUrl] = useState(null);
  const [visibleSamples, setVisibleSamples] = useState([]);
  const [isFetchingSamples, setIsFetchingSamples] = useState(false);
  const [openConfirm, setOpenConfirm] = useState(false); // Confirmation dialog state

  // Load samples from backend on mount
  const loadSamplesFromBackend = async () => {
    try {
      // Add timestamp to prevent caching
      const res = await fetch(`${API_BASE_URL}/list-samples/?t=${Date.now()}`);
      if (res.ok) {
        const data = await res.json();
        const mapped = data.samples.map((s, i) => ({
          ...s,
          url: `${API_BASE_URL}/${s.path}`,
          id: `sample-${i}`,
          displayName: s.name
        }));
        setVisibleSamples(mapped);
      }
    } catch (e) {
      console.error("Failed to list samples:", e);
    }
  };

  React.useEffect(() => {
    loadSamplesFromBackend();
  }, []);

  // Handler to open confirmation dialog
  const handleFetchClick = () => {
    setOpenConfirm(true);
  };

  // Handler to cancel confirmation dialog
  const handleFetchCancel = () => {
    setOpenConfirm(false);
  };

  // Handler to trigger backend download
  const handleFetchConfirmed = async () => {
    setOpenConfirm(false); // Close dialog
    setIsFetchingSamples(true);
    try {
      // Trigger download
      const res = await fetch(`${API_BASE_URL}/download-samples/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: 100 })
      });
      if (res.ok) {
        // Refresh list
        await loadSamplesFromBackend();
      } else {
        alert("Failed to download samples from backend.");
      }
    } catch (e) {
      console.error("Download error:", e);
      alert("Error triggering download.");
    } finally {
      setIsFetchingSamples(false);
    }
  };

  // Map for compatibility with MCP tab (derived from visibleSamples)
  const sampleDataFiles = visibleSamples.map(s => ({ path: s.path, name: s.name }));

  // Load available MCP tools on mount
  React.useEffect(() => {
    const loadMcpTools = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/mcp/tools`);
        if (response.ok) {
          const data = await response.json();
          setMcpAvailableTools(data.tools || defaultMcpTools);
        } else {
          // Fallback to default tools if API fails
          setMcpAvailableTools(defaultMcpTools);
        }
      } catch (err) {
        console.error('Failed to load MCP tools:', err);
        // Fallback to default tools if fetch fails
        setMcpAvailableTools(defaultMcpTools);
      }
    };
    loadMcpTools();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!workflowFile || !inputFile) {
      setError('Please upload or select workflow and input files');
      return;
    }

    // Validate file sizes (prevent empty files)
    if (workflowFile.size === 0) {
      setError('Workflow file is empty');
      return;
    }
    if (inputFile.size === 0) {
      setError('Input file is empty');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    const formData = new FormData();
    formData.append('workflow', workflowFile);
    formData.append('input_artifact', inputFile);
    formData.append('adapter', adapter);
    try {
      // Use direct backend URL
      const response = await fetch(`${API_BASE_URL}/run-workflow/`, {
        method: 'POST',
        body: formData,
      });
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      if (!response.ok) {
        // Extract error detail from API response
        const errorDetail = data?.detail || data?.message || `API error: ${response.status}`;
        throw new Error(errorDetail);
      }
      setResult(data);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Load Sample Handler
  const handleLoadSample = async (sample) => {
    console.log("Loading sample:", sample);

    // 1. Reset State
    setOcrError(null);
    setOcrImage(null);
    setOcrResult(null);

    // 2. Set Preview Immediately (Direct URL)
    setPreviewUrl(sample.url);

    // 3. Try to Fetch Blob (Best Effort)
    try {
      setOcrLoading(true);
      // 'cors' mode to try and get a blob
      const res = await fetch(sample.url, { mode: 'cors' });
      if (!res.ok) throw new Error(`Fetch status: ${res.status}`);

      const blob = await res.blob();
      const file = new File([blob], sample.name || 'sample.png', { type: blob.type });
      setOcrImage(file);
    } catch (e) {
      console.log("Blob fetch failed (CORS), falling back to Server-Side fetch:", e);
      // Do NOT set error. Leave ocrImage null. 
      // The submit handler will detect (ocrImage is null, but previewUrl exists) and send URL.
    } finally {
      setOcrLoading(false);
    }
  };

  const handleAnalyzeQuality = async () => {
    if (!ocrImage && !previewUrl) return;
    setQualityLoading(true);
    setQualityResult(null);
    try {
      const imagePath = ocrImage?.path || previewUrl;
      // If it's a blob URL (previewUrl but no path), we can't easily analyze on backend without upload.
      // For this demo, we restrict to server samples or local paths that the backend can access?
      // Wait, 'previewUrl' for server samples is a full URL. For uploads, it's a blob.
      // Backend 'analyze-quality' expects 'image_path' relative to project root or absolute.
      // If it's a download URL, we might need to handle it.
      // Or strictly support samples for now as requested ("Check if images are OCR Worthy").

      // Simplification: Only support samples for quality check initially, or we need an upload endpoint.
      // Let's assume 'ocrImage.path' exists (Server Sample or Local File Path).
      // If it is a blob upload, we might skip.

      let pathToSend = ocrImage?.path;
      if (!pathToSend && visibleSamples) {
        // Find if previewUrl matches a sample
        const match = visibleSamples.find(s => s.url === previewUrl);
        if (match) pathToSend = match.path;
      }

      if (!pathToSend) {
        alert("Quality analysis currently supports server samples only.");
        setQualityLoading(false);
        return;
      }

      const res = await fetch(`${API_BASE_URL}/analyze-quality`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_path: pathToSend })
      });
      const data = await res.json();
      setQualityResult(data);
    } catch (e) {
      console.error("Quality check failed", e);
    } finally {
      setQualityLoading(false);
    }
  };

  // OCR Handler
  const handleOcrSubmit = async (e) => {
    e.preventDefault();
    setOcrLoading(true);
    setOcrError(null);
    setOcrResult(null);
    const formData = new FormData();

    // Strategy 1: Uploaded File (or successfully fetched blob)
    if (ocrImage) {
      if (ocrImage.path) {
        formData.append('file_path', ocrImage.path); // Local sample
      } else {
        formData.append('image', ocrImage); // Uploaded/Fetched blob
      }
    }
    // Strategy 2: Server-Side Fetch (Fallback for CORS)
    else if (previewUrl) {
      console.log("Using Server-Side Fetch for URL:", previewUrl);
      formData.append('file_path', previewUrl);
    } else {
      setOcrError('Please select an image file or choose a sample');
      setOcrLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/run-ocr/`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('API error: ' + response.status);
      const data = await response.json();
      setOcrResult(data);
    } catch (err) {
      setOcrError(err.message);
    } finally {
      setOcrLoading(false);
    }
  };

  // MCP Tool Call Handler
  const handleMcpCall = async (e) => {
    e.preventDefault();
    setMcpLoading(true);
    setMcpError(null);
    setMcpResult(null);
    try {
      let args;
      try {
        args = JSON.parse(mcpArgs);
      } catch (e) {
        setMcpError(`Invalid JSON arguments: ${e.message}`);
        setMcpLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/mcp/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          method: "tools/call",
          params: {
            name: mcpToolName,
            arguments: args,
          },
          id: 1,
        }),
      });
      if (!response.ok) throw new Error('API error: ' + response.status);
      const data = await response.json();
      setMcpResult(data);
    } catch (err) {
      setMcpError(err.message);
    } finally {
      setMcpLoading(false);
    }
  };

  // Agent Handler
  const handleAgentSubmit = async (e) => {
    e.preventDefault();
    setAgentLoading(true);
    setAgentError(null);
    setAgentResult(null);

    try {
      const formData = new FormData();
      formData.append('prompt', agentPrompt);
      formData.append('model', agentModel);

      const response = await fetch(`${API_BASE_URL}/agent/execute`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('API error: ' + response.status);
      const data = await response.json();

      // Build execution trace from response
      const executionTrace = [];
      let stepNum = 1;

      // Add reasoning steps
      for (let i = 0; i < data.reasoning_steps.length; i++) {
        executionTrace.push({
          step_number: stepNum,
          node_type: 'agent',
          message: `Iteration ${i + 1}: Agent Reasoning`,
          reasoning: data.reasoning_steps[i],
          tool_name: '',
          tool_input: {},
          tool_result: ''
        });
        stepNum++;
      }

      // Add tool calls
      for (const tool_call of data.tool_calls) {
        executionTrace.push({
          step_number: stepNum,
          node_type: 'tool',
          message: `Executing tool: ${tool_call.tool || tool_call.name || 'unknown'}`,
          tool_name: tool_call.tool || tool_call.name || '',
          tool_input: tool_call.input || tool_call.arguments || {},
          tool_result: tool_call.result || '',
          reasoning: ''
        });
        stepNum++;
      }

      setAgentResult({
        ...data,
        execution_trace: executionTrace
      });
    } catch (err) {
      setAgentError(err.message);
    } finally {
      setAgentLoading(false);
    }
  };

  return (
    <div style={{
      background: 'transparent',
      height: '100vh',
      overflow: 'hidden',
      position: 'relative',
      width: '100%',
      fontFamily: 'Inter, sans-serif',
      margin: 0,
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header with Navigation */}
      <div style={{ backgroundColor: 'rgba(0, 0, 0, 0.4)', padding: '20px 0', zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <Typography variant="h4" fontWeight={700} color="#fff" sx={{ textShadow: '0 2px 10px rgba(0,0,0,0.3)', fontWeight: 800, letterSpacing: '-1px', margin: 0 }}>
            🚀 Agentic Platform
          </Typography>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '60px', zIndex: 3 }}>
        <Container maxWidth="md" sx={{ marginTop: '32px', marginBottom: '40px' }}>
          {/* Navigation Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 4 }}>
            <Button
              onClick={() => setActiveView('ocr')}
              variant={activeView === 'ocr' ? 'contained' : 'outlined'}
              size="large"
              sx={{
                minWidth: '150px',
                backgroundColor: activeView === 'ocr' ? '#667eea' : 'transparent',
                borderColor: '#667eea',
                color: activeView === 'ocr' ? '#fff' : '#667eea',
                '&:hover': {
                  backgroundColor: activeView === 'ocr' ? '#5a6fd8' : 'rgba(102, 126, 234, 0.1)',
                  borderColor: '#667eea',
                }
              }}
            >
              📷 OCR Demo
            </Button>
            <Button
              onClick={() => setActiveView('mcp')}
              variant={activeView === 'mcp' ? 'contained' : 'outlined'}
              size="large"
              sx={{
                minWidth: '150px',
                backgroundColor: activeView === 'mcp' ? '#764ba2' : 'transparent',
                borderColor: '#764ba2',
                color: activeView === 'mcp' ? '#fff' : '#764ba2',
                '&:hover': {
                  backgroundColor: activeView === 'mcp' ? '#6b4190' : 'rgba(118, 75, 162, 0.1)',
                  borderColor: '#764ba2',
                }
              }}
            >
              🔧 MCP Test
            </Button>
            <Button
              onClick={() => setActiveView('workflow')}
              variant={activeView === 'workflow' ? 'contained' : 'outlined'}
              size="large"
              sx={{
                minWidth: '150px',
                backgroundColor: activeView === 'workflow' ? '#43e97b' : 'transparent',
                borderColor: '#43e97b',
                color: activeView === 'workflow' ? '#fff' : '#43e97b',
                '&:hover': {
                  backgroundColor: activeView === 'workflow' ? '#3bd66d' : 'rgba(67, 233, 123, 0.1)',
                  borderColor: '#43e97b',
                }
              }}
            >
              ⚙️ Workflow
            </Button>
            <Button
              onClick={() => setActiveView('agent')}
              variant={activeView === 'agent' ? 'contained' : 'outlined'}
              size="large"
              sx={{
                minWidth: '150px',
                backgroundColor: activeView === 'agent' ? '#ff6b6b' : 'transparent',
                borderColor: '#ff6b6b',
                color: activeView === 'agent' ? '#fff' : '#ff6b6b',
                '&:hover': {
                  backgroundColor: activeView === 'agent' ? '#ff5252' : 'rgba(255, 107, 107, 0.1)',
                  borderColor: '#ff6b6b',
                }
              }}
            >
              🤖 Agent
            </Button>
          </Box>

          {/* OCR Demo Section */}
          {activeView === 'ocr' && (
            <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #667eea' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#667eea' }}>📷 OCR Demonstration</Typography>
                  <Button size="small" variant="outlined" startIcon={<span>🏗️</span>} onClick={() => handleOpenArch('ocr')}>
                    View Architecture
                  </Button>
                </Box>


                <LearningBanner
                  concept="API Wrapper Pattern"
                  icon="🔌"
                  codeRef="src/agentic_platform/tools/google_vision_ocr.py"
                  description="This module demonstrates wrapping an external API (Google Vision) as a reusable Tool. The frontend uploads an image or URL, and the Backend API calls the `GoogleVisionOCR` class to return structured text."
                />

                <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Extract text from images using Google Vision API</Typography>


                {/* Quality Analysis Result */}
                {qualityResult && (
                  <Alert severity={qualityResult.score > 80 ? 'success' : qualityResult.score > 40 ? 'warning' : 'error'} sx={{ mt: 2, mb: 2 }}>
                    <Typography variant="subtitle2" fontWeight={700}>
                      OCR Suitability Score: {qualityResult.score}/100 - {qualityResult.verdict}
                    </Typography>
                    <ul style={{ margin: '5px 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
                      {qualityResult.reasoning.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  </Alert>
                )}

                <Box component="form" onSubmit={handleOcrSubmit} sx={{ display: 'grid', gap: 2 }}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button type="submit" variant="contained" color="primary" disabled={ocrLoading || (!ocrImage && !previewUrl)} sx={{ flex: 1, fontWeight: 600, fontSize: '1rem', py: 1.2 }}>
                      {ocrLoading ? <CircularProgress size={24} color="inherit" /> : 'Run OCR Extraction'}
                    </Button>
                    <Button
                      variant="outlined"
                      color="secondary"
                      onClick={handleAnalyzeQuality}
                      disabled={(!ocrImage && !previewUrl) || qualityLoading}
                      sx={{ minWidth: '150px' }}
                      startIcon={qualityLoading ? <CircularProgress size={20} color="inherit" /> : <span>📊</span>}
                    >
                      Check Quality
                    </Button>
                  </Box>

                  <Box>
                    <Button variant="contained" component="label" sx={{ mb: 1, width: '100%' }}>
                      Upload Image File
                      <input type="file" accept="image/*" hidden onChange={e => {
                        const file = e.target.files[0];
                        if (file) {
                          setOcrImage(file);
                          setPreviewUrl(URL.createObjectURL(file));
                        }
                      }} />
                    </Button>
                  </Box>

                  {/* Sample Files for OCR with Scroll & Preview */}
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        📝 Select from Server Samples:
                      </Typography>

                      {/* Confirmation Dialog */}
                      <Dialog
                        open={openConfirm}
                        onClose={handleFetchCancel}
                      >
                        <DialogTitle>{"Download 100 Samples?"}</DialogTitle>
                        <DialogContent>
                          <DialogContentText>
                            This will download 100 images from the internet to the server.
                            The process takes about 40-60 seconds and the UI will be blocked during this time.
                          </DialogContentText>
                        </DialogContent>
                        <DialogActions>
                          <Button onClick={handleFetchCancel}>Cancel</Button>
                          <Button onClick={handleFetchConfirmed} autoFocus variant="contained" color="primary">
                            Yes, Fetch
                          </Button>
                        </DialogActions>
                      </Dialog>

                      <Button
                        variant="contained"
                        color="secondary"
                        size="medium"
                        fullWidth
                        onClick={handleFetchClick}
                        disabled={isFetchingSamples}
                        sx={{ fontSize: '0.9rem', textTransform: 'none', mb: 2, fontWeight: 'bold', border: '2px solid #667eea' }}
                      >
                        {isFetchingSamples ? <CircularProgress size={20} sx={{ mr: 1, color: 'white' }} /> : '⬇️ '}
                        {isFetchingSamples ? 'Downloading 100 Samples...' : 'Fetch 100 Internet Samples (Click Me)'}
                      </Button>
                    </Box>

                    {/* Scrollable Sample List */}
                    <Box
                      scrollable="true"
                      sx={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
                        gap: 1,
                        maxHeight: '150px',
                        overflowY: 'auto',
                        border: '1px solid #eee',
                        p: 1,
                        borderRadius: 1,
                        mb: 2
                      }}
                    >
                      {visibleSamples.map(sample => (
                        <Button
                          key={sample.id}
                          variant="outlined"
                          size="small"
                          onClick={() => handleLoadSample(sample)}
                          sx={{
                            textTransform: 'none',
                            fontSize: '0.75rem',
                            py: 0.5,
                            justifyContent: 'flex-start',
                            color: '#667eea',
                            borderColor: '#667eea',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            backgroundColor: previewUrl === sample.url ? '#e3f2fd' : 'transparent',
                            '&:hover': {
                              backgroundColor: '#e3f2fd',
                              borderColor: '#667eea'
                            }
                          }}
                        >
                          {sample.type === 'external' ? '🌐 ' : '📄 '}
                          {sample.displayName || sample.name}
                        </Button>
                      ))}
                    </Box>

                    {/* Image Preview Pane */}
                    {previewUrl && (
                      <Box sx={{ mt: 2, mb: 2, textAlign: 'center', border: '1px dashed #ccc', borderRadius: 2, p: 2, bgcolor: '#f9f9f9' }}>
                        <Typography variant="caption" color="textSecondary" gutterBottom>
                          Preview (Click 'Run OCR' to process)
                        </Typography>
                        <Box sx={{ mt: 1, mb: 1, maxHeight: '200px', overflow: 'hidden', display: 'flex', justifyContent: 'center' }}>
                          <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%', maxHeight: '200px', objectFit: 'contain' }} />
                        </Box>
                        <Typography variant="caption" sx={{ display: 'block', wordBreak: 'break-all', fontSize: '0.7rem', color: '#888' }}>
                          Source: {previewUrl}
                        </Typography>

                        {/* Status Indicator */}
                        {!ocrImage && !ocrLoading && (
                          <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#2e7d32', fontWeight: 600 }}>
                            ✅ Ready (Server-side fetch mode)
                          </Typography>
                        )}
                        {ocrImage && (
                          <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#1976d2', fontWeight: 600 }}>
                            ✅ Ready (Direct Upload mode)
                          </Typography>
                        )}
                      </Box>
                    )}

                  </Box>
                </Box>
                {ocrError && <Alert severity="error" sx={{ mt: 2 }}>{ocrError}</Alert>}
                {ocrResult && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" fontWeight={600}>
                      OCR Result
                      {ocrResult.confidence > 0 && (
                        <span style={{ fontSize: '0.8em', color: '#4caf50', marginLeft: '10px' }}>
                          (Confidence: {(ocrResult.confidence * 100).toFixed(0)}%)
                        </span>
                      )}
                    </Typography>
                    <Box sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '1rem', overflowX: 'auto', whiteSpace: 'pre-line', maxHeight: '400px', overflowY: 'auto' }}>
                      {ocrResult.formatted_text_lines && ocrResult.formatted_text_lines.length > 0 ? (
                        ocrResult.formatted_text_lines.map((line, idx) => (
                          <div key={idx}>{line}</div>
                        ))
                      ) : (
                        <Box sx={{ color: '#888' }}>
                          {ocrResult.error ? (
                            <span style={{ color: '#f44336' }}>Error: {ocrResult.error}</span>
                          ) : (
                            '[No text detected]'
                          )}
                        </Box>
                      )}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}

          {/* MCP Demo Section */}
          {activeView === 'mcp' && (
            <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #764ba2' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#764ba2' }}>🔧 MCP Tool Tester</Typography>
                  <Button size="small" variant="outlined" startIcon={<span>🏗️</span>} onClick={() => handleOpenArch('mcp')}>
                    View Architecture
                  </Button>
                </Box>


                <LearningBanner
                  concept="Model Context Protocol (MCP)"
                  icon="🛠️"
                  codeRef="src/agentic_platform/tools/tool_registry.py"
                  description="MCP standardizes how AI models interact with server-side tools. This demo also showcases RAG (Retrieval Augmented Generation) where the 'search_knowledge_base' tool retrieves documents to ground the model's response."
                />

                <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Call any MCP-registered tool directly with JSON-RPC 2.0</Typography>

                <Box component="form" onSubmit={handleMcpCall} sx={{ display: 'grid', gap: 2 }}>
                  <FormControl fullWidth>
                    <InputLabel id="mcp-tool-label">Select Tool</InputLabel>
                    <Select
                      labelId="mcp-tool-label"
                      value={mcpToolName}
                      label="Select Tool"
                      onChange={e => setMcpToolName(e.target.value)}
                    >
                      {mcpAvailableTools.map(tool => (
                        <MenuItem key={tool.name} value={tool.name}>{tool.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  {mcpToolName === 'google_vision_ocr' && (
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1, mt: 2 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>Sample Images (Shared with OCR):</Typography>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={handleFetchClick}
                          disabled={isFetchingSamples}
                          sx={{ fontSize: '0.7rem', textTransform: 'none' }}
                        >
                          ⬇️ Fetch 100 Samples
                        </Button>
                      </Box>
                      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, maxHeight: '200px', overflowY: 'auto', border: '1px solid #eee', p: 1, borderRadius: 1 }}>
                        {sampleDataFiles.map(file => (
                          <Button
                            key={file.path}
                            variant="outlined"
                            size="small"
                            onClick={() => setMcpArgs(JSON.stringify({ image_path: file.path }))}
                          >
                            {file.name}
                          </Button>
                        ))}
                      </Box>
                    </Box>
                  )}

                  {mcpToolName === 'search_knowledge_base' && (
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 1, mt: 2 }}>Quick Search Queries:</Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Button variant="outlined" size="small" onClick={() => setMcpArgs(JSON.stringify({ query: 'neural network' }))}>
                          🧠 Neural Network
                        </Button>
                        <Button variant="outlined" size="small" onClick={() => setMcpArgs(JSON.stringify({ query: 'transformer' }))}>
                          🤖 Transformer
                        </Button>
                        <Button variant="outlined" size="small" onClick={() => setMcpArgs(JSON.stringify({ query: 'langgraph' }))}>
                          🕸️ LangGraph
                        </Button>
                      </Box>
                    </Box>
                  )}

                  <TextField
                    label="Tool Arguments (JSON)"
                    multiline
                    rows={4}
                    value={mcpArgs}
                    onChange={e => setMcpArgs(e.target.value)}
                    placeholder='{"image_path": "sample_data/letter.jpg"}'
                    variant="outlined"
                  />
                  <Button type="submit" variant="contained" color="primary" disabled={mcpLoading} sx={{ fontWeight: 600, fontSize: '1rem', py: 1.2 }}>
                    {mcpLoading ? <CircularProgress size={24} color="inherit" /> : 'Call Tool'}
                  </Button>
                </Box>
                {mcpError && <Alert severity="error" sx={{ mt: 2 }}>{mcpError}</Alert>}
                {mcpResult && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" fontWeight={600}>Tool Result</Typography>

                    {/* Smart Parsing for MCP Content */}
                    {mcpResult.result && mcpResult.result.content && Array.isArray(mcpResult.result.content) && mcpResult.result.content.length > 0 ? (
                      <Box sx={{ background: '#e8f5e9', borderRadius: 2, p: 2, mb: 2, borderLeft: '5px solid #4caf50' }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#2e7d32', mb: 1 }}>✅ Parsed Output</Typography>
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                          {mcpResult.result.content[0].text}
                        </Typography>
                      </Box>
                    ) : null}

                    <Box sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', fontFamily: 'monospace', overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
                      <Typography variant="caption" sx={{ display: 'block', mb: 1, color: '#999' }}>Raw JSON-RPC Response:</Typography>
                      {JSON.stringify(mcpResult, null, 2)}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}

          {activeView === 'workflow' && (
            <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #43e97b' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#43e97b' }}>⚙️ Run Workflow</Typography>
                  <Button size="small" variant="outlined" startIcon={<span>🏗️</span>} onClick={() => handleOpenArch('workflow')}>
                    View Architecture
                  </Button>
                </Box>

                <LearningBanner
                  concept="Deterministic State Machine"
                  icon="⚡"
                  codeRef="demo_workflow.yaml"
                  description="Unlike an Agent, a Workflow follows a pre-defined path defined in `demo_workflow.yaml`. We use `LangGraph` to compile a state machine from this YAML conf, ensuring deterministic execution of steps. The 'Input' is a JSON payload injection."
                />



                <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Upload workflow YAML and input JSON to execute</Typography>

                <Box component="form" onSubmit={handleSubmit} sx={{ display: 'grid', gap: 2 }}>

                  {/* Workflow Examples */}
                  <Box sx={{ mb: 1, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, mb: 1, display: 'block', color: '#666' }}>🚀 Quick Start: Load Example Workflow</Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      {Object.keys(WORKFLOW_EXAMPLES).map(key => (
                        <Button
                          key={key}
                          variant="outlined"
                          size="small"
                          onClick={() => {
                            const blob = new Blob([WORKFLOW_EXAMPLES[key]], { type: 'text/yaml' });
                            const file = new File([blob], `${key}_workflow.yaml`, { type: 'text/yaml' });
                            setWorkflowFile(file);
                          }}
                          sx={{ textTransform: 'none', bgcolor: 'white' }}
                        >
                          {key.charAt(0).toUpperCase() + key.slice(1)} Flow
                        </Button>
                      ))}
                    </Box>
                  </Box>

                  <Box>
                    <Button variant="contained" component="label" sx={{ mb: 1, width: '100%' }}>
                      Upload Workflow YAML
                      <input type="file" accept=".yaml,.yml" hidden onChange={e => setWorkflowFile(e.target.files[0])} />
                    </Button>
                    {workflowFile && (
                      <Typography variant="body2" sx={{ color: '#4caf50', fontWeight: 500 }}>
                        ✓ Workflow: {workflowFile.name}
                      </Typography>
                    )}
                  </Box>

                  <Box>
                    <Button variant="contained" component="label" sx={{ mb: 1, width: '100%' }}>
                      Upload Input JSON
                      <input type="file" accept=".json" hidden onChange={e => setInputFile(e.target.files[0])} />
                    </Button>
                    {inputFile && (
                      <Typography variant="body2" sx={{ color: '#4caf50', fontWeight: 500 }}>
                        ✓ Input: {inputFile.name}
                      </Typography>
                    )}
                  </Box>

                  {/* Sample Files for Workflow */}
                  <Box>
                    <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                      📝 Load Sample Files:
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 1 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => {
                          fetch(`${API_BASE_URL}/demo_workflow.yaml`)
                            .then(res => res.text())
                            .then(text => {
                              const file = new File([text], 'demo_workflow.yaml', { type: 'application/x-yaml' });
                              setWorkflowFile(file);
                            })
                            .catch(err => {
                              console.error('Failed to load demo workflow:', err);
                              setError('Failed to load demo workflow');
                            });
                        }}
                        sx={{
                          textTransform: 'none',
                          fontSize: '0.85rem',
                          py: 0.8,
                          justifyContent: 'flex-start',
                          color: '#764ba2',
                          borderColor: '#764ba2',
                          backgroundColor: workflowFile?.name === 'demo_workflow.yaml' ? '#f3e5f5' : 'transparent',
                          '&:hover': {
                            backgroundColor: '#f3e5f5',
                            borderColor: '#764ba2'
                          }
                        }}
                      >
                        {workflowFile?.name === 'demo_workflow.yaml' ? '✓ ' : ''}📄 Demo Workflow (OCR)
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => {
                          fetch(`${API_BASE_URL}/demo_input.json`)
                            .then(res => res.text())
                            .then(text => {
                              const file = new File([text], 'demo_input.json', { type: 'application/json' });
                              setInputFile(file);
                            })
                            .catch(err => {
                              console.error('Failed to load demo input:', err);
                              setError('Failed to load demo input');
                            });
                        }}
                        sx={{
                          textTransform: 'none',
                          fontSize: '0.85rem',
                          py: 0.8,
                          justifyContent: 'flex-start',
                          color: '#764ba2',
                          borderColor: '#764ba2',
                          backgroundColor: inputFile?.name === 'demo_input.json' ? '#f3e5f5' : 'transparent',
                          '&:hover': {
                            backgroundColor: '#f3e5f5',
                            borderColor: '#764ba2'
                          }
                        }}
                      >
                        {inputFile?.name === 'demo_input.json' ? '✓ ' : ''}📄 Demo Input (Sample Data)
                      </Button>
                    </Box>
                  </Box>

                  <FormControl fullWidth>
                    <InputLabel id="adapter-label">Adapter</InputLabel>
                    <Select
                      labelId="adapter-label"
                      value={adapter}
                      label="Adapter"
                      onChange={e => setAdapter(e.target.value)}
                    >
                      <MenuItem value="mcp">MCP</MenuItem>
                      <MenuItem value="langgraph">LangGraph</MenuItem>
                    </Select>
                  </FormControl>
                  <Button type="submit" variant="contained" color="primary" disabled={loading}>
                    {loading ? <CircularProgress size={24} color="inherit" /> : 'Run Workflow'}
                  </Button>
                </Box>
                {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

                {result && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Workflow Results</Typography>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" fontWeight={600}>Result Output</Typography>
                      <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>
                        {result.result ? JSON.stringify(result.result, null, 2) : 'No result'}
                      </Box>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" fontWeight={600}>Tool Results</Typography>
                      <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>
                        {result.tool_results ? JSON.stringify(result.tool_results, null, 2) : 'No tool results'}
                      </Box>
                    </Box>

                    <Box>
                      <Typography variant="subtitle2" fontWeight={600}>Audit Log</Typography>
                      <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>
                        {result.audit_log ? JSON.stringify(result.audit_log, null, 2) : 'No audit log'}
                      </Box>
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}

          {/* LangGraph Agent Demo Section */}
          {activeView === 'agent' && (
            <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #ff6b6b' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#ff6b6b' }}>🤖 LangGraph Agent Reasoning</Typography>
                  <Button size="small" variant="outlined" startIcon={<span>🏗️</span>} onClick={() => handleOpenArch('agent')}>
                    View Architecture
                  </Button>
                </Box>

                <LearningBanner
                  concept="ReAct Loop (Reason + Act)"
                  icon="🧠"
                  codeRef="src/agentic_platform/agent.py"
                  description="This is an Autonomous Agent. It uses a Large Language Model (LLM) to **Reason** about your task, decide which **Tool** to call, execute it, and observe the result."
                />



                <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Watch the agent reason, route decisions, and execute tools in real-time</Typography>

                <Box component="form" onSubmit={handleAgentSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>

                  <Box>
                    <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>Quick Prompts:</Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                      {AGENT_PROMPTS.map((p, i) => (
                        <Button
                          key={i}
                          variant="outlined"
                          size="small"
                          onClick={() => setAgentPrompt(p)}
                          sx={{ textTransform: 'none', fontSize: '0.75rem' }}
                        >
                          {p.length > 20 ? p.substring(0, 20) + '...' : p}
                        </Button>
                      ))}
                    </Box>
                  </Box>

                  <TextField
                    label="Prompt"
                    multiline
                    rows={4}
                    value={agentPrompt}
                    onChange={(e) => setAgentPrompt(e.target.value)}
                    disabled={agentLoading}
                    fullWidth
                  />

                  <FormControl fullWidth>
                    <InputLabel>Model</InputLabel>
                    <Select
                      value={agentModel}
                      onChange={(e) => setAgentModel(e.target.value)}
                      label="Model"
                      disabled={agentLoading}
                    >
                      <MenuItem value="mock-llm">Mock LLM (Free)</MenuItem>
                      <MenuItem value="claude-3.5-sonnet">Claude 3.5 Sonnet</MenuItem>
                      <MenuItem value="gpt-4">GPT-4</MenuItem>
                    </Select>
                  </FormControl>

                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={agentLoading}
                    sx={{ fontWeight: 600, fontSize: '1rem', py: 1.2, backgroundColor: '#ff6b6b', '&:hover': { backgroundColor: '#ff5252' } }}
                  >
                    {agentLoading ? <CircularProgress size={24} color="inherit" /> : 'Execute Agent'}
                  </Button>
                </Box>

                {agentError && <Alert severity="error" sx={{ mt: 2 }}>{agentError}</Alert>}

                {agentResult && (
                  <Box sx={{ mt: 3 }}>
                    {/* Status Bar */}
                    <Box sx={{
                      background: agentResult.status === 'success' ? '#e8f5e9' : '#fff3e0',
                      borderLeft: `4px solid ${agentResult.status === 'success' ? '#4caf50' : '#ff9800'}`,
                      p: 2,
                      borderRadius: 1,
                      mb: 2
                    }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        Status: <span style={{ textTransform: 'uppercase', fontWeight: 700 }}>{agentResult.status}</span>
                      </Typography>
                      <Typography variant="body2">
                        Iterations: {agentResult.iterations} | Tool Calls: {agentResult.tool_calls?.length || 0}
                      </Typography>
                    </Box>

                    {/* Execution Steps Timeline */}
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>⏱️ Execution Timeline</Typography>
                    <Box sx={{
                      border: '1px solid #e0e0e0',
                      borderRadius: 1,
                      overflow: 'hidden',
                      mb: 3
                    }}>
                      {agentResult.execution_trace && agentResult.execution_trace.length > 0 ? (
                        agentResult.execution_trace.map((step, idx) => (
                          <Box key={idx}>
                            <Box
                              onClick={() => setExpandedStep(expandedStep === idx ? null : idx)}
                              sx={{
                                background: step.node_type === 'agent' ? '#e3f2fd' : step.node_type === 'tool' ? '#fff3e0' : '#f3e5f5',
                                p: 2,
                                borderBottom: '1px solid #e0e0e0',
                                borderLeft: `4px solid ${step.node_type === 'agent' ? '#2196f3' : step.node_type === 'tool' ? '#ff9800' : '#9c27b0'}`,
                                cursor: 'pointer',
                                '&:hover': { background: step.node_type === 'agent' ? '#bbdefb' : step.node_type === 'tool' ? '#ffe0b2' : '#e1bee7' },
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between'
                              }}
                            >
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: step.node_type === 'agent' ? '#1565c0' : step.node_type === 'tool' ? '#e65100' : '#4a148c' }}>
                                  Step {step.step_number}: {
                                    step.node_type === 'agent' ? '🧠 Agent Reasoning' :
                                      step.node_type === 'tool' ? '🛠️ Tool Execution' :
                                        '🚦 Router Decision'
                                  }
                                </Typography>
                                <Typography variant="body2" color="textSecondary">{step.message}</Typography>
                              </Box>
                              <Typography sx={{ color: '#999', ml: 2, fontWeight: 700 }}>
                                {expandedStep === idx ? '▼' : '▶'}
                              </Typography>
                            </Box>

                            {/* Expanded Details */}
                            {expandedStep === idx && (
                              <Box sx={{ background: '#f9f9f9', p: 2, borderBottom: '1px solid #e0e0e0' }}>
                                {step.reasoning && (
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Reasoning:</Typography>
                                    <Box sx={{ background: '#fff', p: 1.5, borderRadius: 1, fontSize: '0.85rem', whiteSpace: 'pre-wrap', fontFamily: 'monospace', overflowX: 'auto' }}>
                                      {step.reasoning}
                                    </Box>
                                  </Box>
                                )}
                                {step.tool_name && (
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Tool: {step.tool_name}</Typography>
                                    <Box sx={{ background: '#fff', p: 1.5, borderRadius: 1 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 600 }}>Input:</Typography>
                                      <pre style={{ fontSize: '0.75rem', overflow: 'auto', margin: '8px 0' }}>
                                        {JSON.stringify(step.tool_input, null, 2)}
                                      </pre>
                                      {step.tool_result && (
                                        <>
                                          <Typography variant="body2" sx={{ fontWeight: 600, mt: 1 }}>Result:</Typography>
                                          <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: '150px', margin: '8px 0' }}>
                                            {typeof step.tool_result === 'string' ? step.tool_result : JSON.stringify(step.tool_result, null, 2)}
                                          </pre>
                                        </>
                                      )}
                                    </Box>
                                  </Box>
                                )}
                              </Box>
                            )}
                          </Box>
                        ))
                      ) : (
                        <Box sx={{ p: 2, color: '#999' }}>No execution steps to display</Box>
                      )}
                    </Box>

                    {/* Final Output */}
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>✅ Final Output</Typography>
                    <Box sx={{ background: '#f6f8fa', borderRadius: 1, p: 2, fontSize: '0.95rem', whiteSpace: 'pre-wrap', mb: 3 }}>
                      {agentResult.final_output || '[No output]'}
                    </Box>

                    {/* Reasoning Steps */}
                    {agentResult.reasoning_steps && agentResult.reasoning_steps.length > 0 && (
                      <>
                        <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>📝 All Reasoning Steps</Typography>
                        <Box sx={{ background: '#f6f8fa', borderRadius: 1, p: 2 }}>
                          {agentResult.reasoning_steps.map((step, idx) => (
                            <Box key={idx} sx={{ mb: 1.5, pb: 1.5, borderBottom: idx < agentResult.reasoning_steps.length - 1 ? '1px solid #ddd' : 'none' }}>
                              <Typography variant="caption" sx={{ fontWeight: 600, color: '#ff6b6b' }}>Step {idx + 1}:</Typography>
                              <Typography variant="body2" sx={{ mt: 0.5 }}>{step}</Typography>
                            </Box>
                          ))}
                        </Box>
                      </>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Container>
        {/* Architecture Diagram Modal */}
        <Dialog
          open={archModalOpen}
          onClose={() => setArchModalOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <span>🏗️</span> System Architecture
          </DialogTitle>
          <DialogContent dividers>
            {currentDiagram && <MermaidDiagram chart={currentDiagram} />}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setArchModalOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </div>
    </div>
  );
}

export default App;
