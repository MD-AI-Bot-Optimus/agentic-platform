import React, { useState } from 'react';
import { Container, Box, Typography, Card, CardContent, Button, TextField, Select, MenuItem, InputLabel, FormControl, Alert, CircularProgress, Paper } from '@mui/material';

function App() {
  // Active view state
  const [activeView, setActiveView] = useState('ocr');

  // Workflow state
  const [workflowFile, setWorkflowFile] = useState(null);
  const [inputFile, setInputFile] = useState(null);
  const [adapter, setAdapter] = useState('mcp');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // OCR demo state
  const [ocrImage, setOcrImage] = useState(null);
  const [ocrResult, setOcrResult] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrError, setOcrError] = useState(null);

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
  const [agentResult, setAgentResult] = useState(null);
  const [agentLoading, setAgentLoading] = useState(false);
  const [agentError, setAgentError] = useState(null);
  
  // Sample data files for quick selection
  const sampleDataFiles = [
    { path: 'sample_data/letter.jpg', name: 'Letter (handwritten)' },
    { path: 'sample_data/handwriting.jpg', name: 'Handwriting Sample' },
    { path: 'sample_data/numbers_gs150.jpg', name: 'Numbers Document' },
    { path: 'sample_data/stock_gs200.jpg', name: 'Stock Image' },
    { path: 'sample_data/ocr_sample_plaid.jpg', name: 'Plaid Pattern' },
  ];

  // Load available MCP tools on mount
  React.useEffect(() => {
    const loadMcpTools = async () => {
      try {
        const apiUrl = window.location.origin;
        const response = await fetch(`${apiUrl}/mcp/tools`);
        if (response.ok) {
          const data = await response.json();
          setMcpAvailableTools(data.tools || []);
        }
      } catch (err) {
        console.error('Failed to load MCP tools:', err);
      }
    };
    loadMcpTools();
  }, []);

  // OCR Handler
  const handleOcrSubmit = async (e) => {
    e.preventDefault();
    setOcrLoading(true);
    setOcrError(null);
    setOcrResult(null);
    const formData = new FormData();
    formData.append('image', ocrImage);
    try {
      const apiUrl = window.location.origin;
      const response = await fetch(`${apiUrl}/run-ocr/`, {
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

  // Workflow Handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    const formData = new FormData();
    formData.append('workflow', workflowFile);
    formData.append('input_artifact', inputFile);
    formData.append('adapter', adapter);
    try {
      const apiUrl = window.location.origin;
      const response = await fetch(`${apiUrl}/run-workflow/`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('API error: ' + response.status);
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // MCP Tool Call Handler
  const handleMcpCall = async (e) => {
    e.preventDefault();
    setMcpLoading(true);
    setMcpError(null);
    setMcpResult(null);
    try {
      let args = {};
      try {
        args = JSON.parse(mcpArgs);
      } catch {
        throw new Error('Invalid JSON in arguments');
      }
      const apiUrl = window.location.origin;
      const response = await fetch(`${apiUrl}/mcp/call-tool`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool: mcpToolName, args }),
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
    const formData = new FormData();
    formData.append('prompt', agentPrompt);
    formData.append('model', agentModel);
    try {
      const apiUrl = window.location.origin;
      const response = await fetch(`${apiUrl}/agent/execute`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('API error: ' + response.status);
      const data = await response.json();
      setAgentResult(data);
    } catch (err) {
      setAgentError(err.message);
    } finally {
      setAgentLoading(false);
    }
  };

  return (
    <div className="highway-bg" style={{ 
      backgroundImage: 'url(/magicalmajestichighway1.jpg)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed',
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
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <Typography variant="h4" fontWeight={700} color="#fff" sx={{ textShadow: '0 2px 10px rgba(0,0,0,0.3)', fontWeight: 800, letterSpacing: '-1px', margin: 0 }}>
            🚀 Agentic Platform
          </Typography>
          <div style={{ display: 'flex', gap: '10px' }}>
            <Button
              onClick={() => setActiveView('ocr')}
              variant={activeView === 'ocr' ? 'contained' : 'outlined'}
              sx={{
                color: activeView === 'ocr' ? '#fff' : '#fff',
                borderColor: '#fff',
                backgroundColor: activeView === 'ocr' ? 'rgba(255,255,255,0.2)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  borderColor: '#fff',
                }
              }}
            >
              📷 OCR Demo
            </Button>
            <Button
              onClick={() => setActiveView('mcp')}
              variant={activeView === 'mcp' ? 'contained' : 'outlined'}
              sx={{
                color: activeView === 'mcp' ? '#fff' : '#fff',
                borderColor: '#fff',
                backgroundColor: activeView === 'mcp' ? 'rgba(255,255,255,0.2)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  borderColor: '#fff',
                }
              }}
            >
              🔧 MCP Tools
            </Button>
            <Button
              onClick={() => setActiveView('agent')}
              variant={activeView === 'agent' ? 'contained' : 'outlined'}
              sx={{
                color: activeView === 'agent' ? '#fff' : '#fff',
                borderColor: '#fff',
                backgroundColor: activeView === 'agent' ? 'rgba(255,255,255,0.2)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  borderColor: '#fff',
                }
              }}
            >
              🤖 LLM Agent
            </Button>
            <Button
              onClick={() => setActiveView('workflow')}
              variant={activeView === 'workflow' ? 'contained' : 'outlined'}
              sx={{
                color: activeView === 'workflow' ? '#fff' : '#fff',
                borderColor: '#fff',
                backgroundColor: activeView === 'workflow' ? 'rgba(255,255,255,0.2)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  borderColor: '#fff',
                }
              }}
            >
              ⚙️ Workflow
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '60px', zIndex: 3 }}>
        <Container maxWidth="md" sx={{ marginTop: '32px', marginBottom: '40px' }}>
            
            {/* OCR Demo Section */}
            {activeView === 'ocr' && (
              <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #667eea' }}>
                <CardContent>
                  <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#667eea' }}>📷 OCR Demonstration</Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Extract text from images using Google Vision API</Typography>
                  
                  <Box component="form" onSubmit={handleOcrSubmit} sx={{ display: 'grid', gap: 2 }}>
                    <Button variant="contained" component="label">
                      Upload Image for OCR
                      <input type="file" accept="image/*" hidden onChange={e => setOcrImage(e.target.files[0])} />
                    </Button>
                    <Button type="submit" variant="contained" color="primary" disabled={ocrLoading || !ocrImage}>
                      {ocrLoading ? <CircularProgress size={24} color="inherit" /> : 'Run OCR'}
                    </Button>
                  </Box>
                  {ocrError && <Alert severity="error" sx={{ mt: 2 }}>{ocrError}</Alert>}
                  {ocrResult && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" fontWeight={600}>OCR Result</Typography>
                      <Box sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '1rem', overflowX: 'auto', whiteSpace: 'pre-line', maxHeight: '400px', overflowY: 'auto' }}>
                        {ocrResult.formatted_text_lines && ocrResult.formatted_text_lines.length > 0 ? (
                          ocrResult.formatted_text_lines.map((line, idx) => (
                            <div key={idx}>{line}</div>
                          ))
                        ) : (
                          <span style={{ color: '#888' }}>[No text detected]</span>
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
                  <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#764ba2' }}>🔧 MCP Tool Tester</Typography>
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

                    {mcpAvailableTools.find(t => t.name === mcpToolName) && (
                      <Box sx={{ background: '#e3f2fd', p: 2, borderRadius: 1 }}>
                        <Typography variant="body2">
                          <strong>Description:</strong> {mcpAvailableTools.find(t => t.name === mcpToolName).description}
                        </Typography>
                      </Box>
                    )}

                    {mcpToolName === 'google_vision_ocr' && (
                      <Box>
                        <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>Sample Files:</Typography>
                        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
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

                    <TextField
                      label="Tool Arguments (JSON)"
                      multiline
                      rows={4}
                      value={mcpArgs}
                      onChange={e => setMcpArgs(e.target.value)}
                      variant="outlined"
                    />

                    <Button type="submit" variant="contained" color="primary" disabled={mcpLoading}>
                      {mcpLoading ? <CircularProgress size={24} color="inherit" /> : 'Call Tool'}
                    </Button>
                  </Box>
                  {mcpError && <Alert severity="error" sx={{ mt: 2 }}>{mcpError}</Alert>}
                  {mcpResult && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" fontWeight={600}>Tool Result</Typography>
                      <Box sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', fontFamily: 'monospace', overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
                        {JSON.stringify(mcpResult, null, 2)}
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}

            {/* LangGraph Agent Section */}
            {activeView === 'agent' && (
              <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #f5576c' }}>
                <CardContent>
                  <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#f5576c' }}>🤖 LLM Agent</Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Autonomous reasoning with Claude, GPT-4, Gemini, or mock LLM</Typography>

                  <Box component="form" onSubmit={handleAgentSubmit} sx={{ display: 'grid', gap: 2 }}>
                    <FormControl fullWidth>
                      <InputLabel id="agent-model-label">Select Model</InputLabel>
                      <Select
                        labelId="agent-model-label"
                        value={agentModel}
                        label="Select Model"
                        onChange={e => setAgentModel(e.target.value)}
                      >
                        <MenuItem value="mock-llm">Mock LLM (Free, Testing)</MenuItem>
                        <MenuItem value="claude-3.5-sonnet">Claude 3.5 Sonnet</MenuItem>
                        <MenuItem value="gpt-4-turbo">GPT-4 Turbo</MenuItem>
                        <MenuItem value="gemini-1.5-pro">Gemini 1.5 Pro</MenuItem>
                      </Select>
                    </FormControl>

                    <TextField
                      label="Prompt"
                      multiline
                      rows={4}
                      value={agentPrompt}
                      onChange={e => setAgentPrompt(e.target.value)}
                      placeholder="Enter your query for the agent..."
                      variant="outlined"
                    />

                    <Button 
                      type="submit" 
                      variant="contained" 
                      color="primary" 
                      disabled={agentLoading || !agentPrompt}
                    >
                      {agentLoading ? <CircularProgress size={24} color="inherit" /> : 'Execute Agent'}
                    </Button>
                  </Box>

                  {agentError && <Alert severity="error" sx={{ mt: 2 }}>{agentError}</Alert>}

                  {agentResult && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" fontWeight={600}>Agent Response</Typography>
                      
                      <Box sx={{ mt: 2, p: 2, background: agentResult.status === 'success' ? '#e8f5e9' : '#fff3e0', borderRadius: 1, borderLeft: `4px solid ${agentResult.status === 'success' ? '#4caf50' : '#ff9800'}` }}>
                        <Typography variant="body2"><strong>Status:</strong> {agentResult.status}</Typography>
                        <Typography variant="body2"><strong>Iterations:</strong> {agentResult.iterations}</Typography>
                        <Typography variant="body2"><strong>Model:</strong> {agentResult.model_used}</Typography>
                      </Box>

                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" fontWeight={600}>Final Output</Typography>
                        <Box sx={{ background: '#f6f8fa', borderRadius: 1, p: 2, fontSize: '0.95rem', fontStyle: 'italic', borderLeft: '3px solid #f5576c' }}>
                          {agentResult.final_output}
                        </Box>
                      </Box>

                      {agentResult.reasoning_steps && agentResult.reasoning_steps.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" fontWeight={600}>Reasoning Steps ({agentResult.reasoning_steps.length})</Typography>
                          <Box sx={{ background: '#f6f8fa', borderRadius: 1, p: 2, fontSize: '0.85rem', fontFamily: 'monospace', maxHeight: '300px', overflowY: 'auto' }}>
                            {agentResult.reasoning_steps.map((step, idx) => {
                              const stepText = typeof step === 'string' ? step : JSON.stringify(step);
                              return (
                                <div key={idx} style={{ marginBottom: '8px', paddingBottom: '8px', borderBottom: '1px solid #e0e0e0', wordBreak: 'break-word' }}>
                                  <span style={{ color: '#f5576c', fontWeight: 600 }}>Step {idx + 1}:</span> {stepText.length > 100 ? stepText.substring(0, 100) + '...' : stepText}
                                </div>
                              );
                            })}
                          </Box>
                        </Box>
                      )}

                      {agentResult.tool_calls && agentResult.tool_calls.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" fontWeight={600}>Tools Used ({agentResult.tool_calls.length})</Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                            {agentResult.tool_calls.map((call, idx) => (
                              <Box key={idx} sx={{ background: '#ffe0e6', borderRadius: 1, px: 2, py: 0.5, fontSize: '0.85rem', color: '#f5576c', fontWeight: 500 }}>
                                🔧 {call.tool}
                              </Box>
                            ))}
                          </Box>
                        </Box>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Workflow Demo Section */}
            {activeView === 'workflow' && (
              <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #43e97b' }}>
                <CardContent>
                  <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#43e97b' }}>⚙️ Run Workflow</Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Upload workflow YAML and input JSON to execute</Typography>

                  <Box component="form" onSubmit={handleSubmit} sx={{ display: 'grid', gap: 2 }}>
                    <Button variant="contained" component="label">
                      Upload Workflow YAML
                      <input type="file" accept=".yaml,.yml" hidden onChange={e => setWorkflowFile(e.target.files[0])} />
                    </Button>
                    <Button variant="contained" component="label">
                      Upload Input JSON
                      <input type="file" accept=".json" hidden onChange={e => setInputFile(e.target.files[0])} />
                    </Button>
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
                          {JSON.stringify(result.result, null, 2)}
                        </Box>
                      </Box>

                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" fontWeight={600}>Tool Results</Typography>
                        <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>
                          {JSON.stringify(result.tool_results, null, 2)}
                        </Box>
                      </Box>

                      <Box>
                        <Typography variant="subtitle2" fontWeight={600}>Audit Log</Typography>
                        <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>
                          {JSON.stringify(result.audit_log, null, 2)}
                        </Box>
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Container>
        </div>
      </div>
    </div>
  );
}

export default App;
