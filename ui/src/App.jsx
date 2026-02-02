

import React, { useState } from 'react';
import { Container, Box, Typography, Card, CardContent, Button, TextField, Select, MenuItem, InputLabel, FormControl, Alert, CircularProgress, Grid } from '@mui/material';

// Modern art background styles
const modernArtStyle = {
  background: `
    linear-gradient(135deg, #667eea 0%, #764ba2 25%),
    linear-gradient(225deg, #f093fb 0%, #f5576c 25%),
    linear-gradient(315deg, #4facfe 0%, #00f2fe 25%),
    linear-gradient(45deg, #43e97b 0%, #38f9d7 25%)
  `,
  backgroundSize: '400% 400%',
  animation: 'gradientShift 15s ease infinite',
  position: 'relative',
};

// Add global styles for background
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes floatIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
  }
`;
document.head.appendChild(styleSheet);

function App() {
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
      if (!response.ok) throw new Error('OCR API error: ' + response.status);
      const data = await response.json();
      setOcrResult(data.tool_results && data.tool_results[0] && data.tool_results[0].result);
    } catch (err) {
      setOcrError(err.message);
    } finally {
      setOcrLoading(false);
    }
  };

  const handleMcpCall = async (e) => {
    e.preventDefault();
    setMcpLoading(true);
    setMcpError(null);
    try {
      let args;
      try {
        args = JSON.parse(mcpArgs);
      } catch (e) {
        setMcpError(`Invalid JSON arguments: ${e.message}`);
        setMcpLoading(false);
        return;
      }

      const apiUrl = window.location.origin;
      const response = await fetch(`${apiUrl}/mcp/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: mcpToolName,
            arguments: args,
          },
          id: 1,
        }),
      });

      const data = await response.json();
      setMcpResult(data);
      if (data.error) {
        setMcpError(data.error.message);
      }
    } catch (err) {
      setMcpError(err.message);
    } finally {
      setMcpLoading(false);
    }
  };

  const handleAgentSubmit = async (e) => {
    e.preventDefault();
    setAgentLoading(true);
    setAgentError(null);
    setAgentResult(null);
    try {
      const formData = new FormData();
      formData.append('prompt', agentPrompt);
      formData.append('model', agentModel);

      const apiUrl = window.location.origin;
      const response = await fetch(`${apiUrl}/agent/execute`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error(`Agent API error: ${response.status}`);
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
      <div style={{ backgroundColor: 'rgba(0, 0, 0, 0.3)', padding: '16px 0', zIndex: 100 }}>
        <Typography variant="h3" align="center" fontWeight={700} color="#fff" sx={{ textShadow: '0 2px 10px rgba(0,0,0,0.2)', fontWeight: 800, letterSpacing: '-1px', margin: 0 }}>
          Agentic Platform
        </Typography>
      </div>
      <div className="highway-content" style={{ position: 'relative', zIndex: 3, paddingBottom: '500px', flex: 1, overflowY: 'auto' }}>
        <Container maxWidth="md" sx={{ marginTop: '16px', display: 'flex', justifyContent: 'center', width: '100%' }}>
          <Grid container spacing={3} sx={{ width: '100%', maxWidth: '1200px' }}>
            {/* OCR Demo Section */}
            <Grid item xs={12} sm={6}>
              <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, height: '100%' }}>
                <CardContent>
                <Typography variant="h5" fontWeight={600} gutterBottom>OCR Demo</Typography>
                <Box component="form" onSubmit={handleOcrSubmit} sx={{ display: 'grid', gap: 2 }}>
                  <Button variant="contained" component="label" sx={{ mb: 1 }}>
                    Upload Image for OCR
                    <input type="file" accept="image/*" hidden onChange={e => setOcrImage(e.target.files[0])} required />
                  </Button>
                  <Button type="submit" variant="contained" color="primary" disabled={ocrLoading || !ocrImage} sx={{ fontWeight: 600, fontSize: '1rem', py: 1.2 }}>
                    {ocrLoading ? <CircularProgress size={24} color="inherit" /> : 'Run OCR'}
                  </Button>
                </Box>
                {ocrError && <Alert severity="error" sx={{ mt: 2 }}>{ocrError}</Alert>}
                {ocrResult && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" fontWeight={600}>OCR Result</Typography>
                    <Box sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '1rem', overflowX: 'auto', whiteSpace: 'pre-line' }}>
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
            </Grid>

            {/* MCP Demo Section */}
            <Grid item xs={12} sm={6}>
              <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderLeft: '4px solid #667eea', height: '100%' }}>
                <CardContent>
                  <Typography variant="h5" fontWeight={600} gutterBottom>MCP Tool Tester</Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    Call any MCP-registered tool directly with JSON-RPC 2.0
                  </Typography>
                  <Box component="form" onSubmit={handleMcpCall} sx={{ display: 'grid', gap: 2 }}>
                    {/* Tool Selector */}
                    <FormControl fullWidth>
                      <InputLabel id="mcp-tool-label">Select Tool</InputLabel>
                      <Select
                        labelId="mcp-tool-label"
                        value={mcpToolName}
                        label="Select Tool"
                        onChange={e => setMcpToolName(e.target.value)}
                      >
                        {mcpAvailableTools.map(tool => (
                          <MenuItem key={tool.name} value={tool.name}>
                            {tool.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    {/* Tool Description */}
                    {mcpAvailableTools.find(t => t.name === mcpToolName) && (
                      <Box sx={{ background: '#e3f2fd', p: 2, borderRadius: 1, fontSize: '0.9rem' }}>
                        <Typography variant="body2">
                          <strong>Description:</strong> {mcpAvailableTools.find(t => t.name === mcpToolName).description}
                        </Typography>
                      </Box>
                    )}

                    {/* Sample Data File Shortcuts (for google_vision_ocr) */}
                    {mcpToolName === 'google_vision_ocr' && (
                      <Box>
                        <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                          Sample Files:
                        </Typography>
                        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                          {sampleDataFiles.map(file => (
                            <Button
                              key={file.path}
                              variant="outlined"
                              size="small"
                              onClick={() => setMcpArgs(JSON.stringify({ image_path: file.path }))}
                              sx={{ 
                                textTransform: 'none',
                                fontSize: '0.85rem',
                                py: 0.8,
                                justifyContent: 'flex-start',
                                color: '#667eea',
                                borderColor: '#667eea',
                                '&:hover': { 
                                  backgroundColor: '#e3f2fd',
                                  borderColor: '#667eea'
                                }
                              }}
                            >
                              📄 {file.name}
                            </Button>
                          ))}
                        </Box>
                      </Box>
                    )}

                    {/* Arguments Input */}
                    <TextField
                      label="Tool Arguments (JSON)"
                      multiline
                      rows={4}
                      value={mcpArgs}
                      onChange={e => setMcpArgs(e.target.value)}
                      placeholder='{"image_path": "sample_data/letter.jpg"}'
                      variant="outlined"
                      fullWidth
                      sx={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
                    />

                    {/* Call Button */}
                    <Button 
                      type="submit" 
                      variant="contained" 
                      color="primary" 
                      disabled={mcpLoading} 
                      sx={{ fontWeight: 600, fontSize: '1rem', py: 1.2 }}
                    >
                      {mcpLoading ? <CircularProgress size={24} color="inherit" /> : 'Call Tool'}
                    </Button>
                  </Box>

                  {/* Error Display */}
                  {mcpError && <Alert severity="error" sx={{ mt: 2 }}>{mcpError}</Alert>}

                  {/* Result Display */}
                  {mcpResult && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" fontWeight={600}>MCP Response</Typography>
                      <Box sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', fontFamily: 'monospace', maxHeight: '400px', overflowY: 'auto' }}>
                        <pre>{JSON.stringify(mcpResult, null, 2)}</pre>
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* LangGraph Agent Demo Section */}
            <Grid item xs={12} sm={6}>
              <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderLeft: '4px solid #43e97b', height: '100%' }}>
                <CardContent>
                  <Typography variant="h5" fontWeight={600} gutterBottom>🤖 LangGraph Agent</Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    Autonomous reasoning agent with multi-step tool orchestration
                  </Typography>
                  <Box component="form" onSubmit={handleAgentSubmit} sx={{ display: 'grid', gap: 2 }}>
                    {/* Agent Prompt Input */}
                    <TextField
                      label="Agent Prompt"
                      multiline
                      rows={3}
                      value={agentPrompt}
                      onChange={e => setAgentPrompt(e.target.value)}
                      placeholder="Ask the agent to do something..."
                      fullWidth
                    />

                    {/* Model Selection */}
                    <FormControl fullWidth>
                      <InputLabel>LLM Model</InputLabel>
                      <Select
                        value={agentModel}
                        label="LLM Model"
                        onChange={e => setAgentModel(e.target.value)}
                      >
                        <MenuItem value="mock-llm">Mock LLM (Free/Demo)</MenuItem>
                        <MenuItem value="claude-3.5-sonnet">Claude 3.5 Sonnet</MenuItem>
                        <MenuItem value="gpt-4">GPT-4</MenuItem>
                      </Select>
                    </FormControl>

                    {/* Submit Button */}
                    <Button 
                      type="submit" 
                      variant="contained" 
                      color="primary" 
                      disabled={agentLoading || !agentPrompt} 
                      sx={{ fontWeight: 600, fontSize: '1rem', py: 1.2 }}
                    >
                      {agentLoading ? <CircularProgress size={24} color="inherit" /> : 'Execute Agent'}
                    </Button>
                  </Box>

                  {/* Error Display */}
                  {agentError && <Alert severity="error" sx={{ mt: 2 }}>{agentError}</Alert>}

                  {/* Agent Result Display */}
                  {agentResult && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" fontWeight={600}>Agent Response</Typography>
                      
                      {/* Status */}
                      <Box sx={{ mt: 2, p: 2, background: agentResult.status === 'success' ? '#e8f5e9' : '#fff3e0', borderRadius: 1, borderLeft: `4px solid ${agentResult.status === 'success' ? '#4caf50' : '#ff9800'}` }}>
                        <Typography variant="body2"><strong>Status:</strong> {agentResult.status}</Typography>
                        <Typography variant="body2"><strong>Iterations:</strong> {agentResult.iterations}</Typography>
                      </Box>

                      {/* Final Output */}
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" fontWeight={600}>Final Output</Typography>
                        <Box sx={{ background: '#f6f8fa', borderRadius: 1, p: 2, fontSize: '0.95rem', fontStyle: 'italic', borderLeft: '3px solid #667eea' }}>
                          {agentResult.final_output}
                        </Box>
                      </Box>

                      {/* Reasoning Steps */}
                      {agentResult.reasoning_steps && agentResult.reasoning_steps.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" fontWeight={600}>Reasoning Steps ({agentResult.reasoning_steps.length})</Typography>
                          <Box sx={{ background: '#f6f8fa', borderRadius: 1, p: 2, fontSize: '0.85rem', fontFamily: 'monospace', maxHeight: '200px', overflowY: 'auto' }}>
                            {agentResult.reasoning_steps.map((step, idx) => (
                              <div key={idx} style={{ marginBottom: '8px', paddingBottom: '8px', borderBottom: '1px solid #e0e0e0' }}>
                                <span style={{ color: '#667eea', fontWeight: 600 }}>Step {idx + 1}:</span> {step.substring(0, 100)}...
                              </div>
                            ))}
                          </Box>
                        </Box>
                      )}

                      {/* Tool Calls */}
                      {agentResult.tool_calls && agentResult.tool_calls.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" fontWeight={600}>Tools Used ({agentResult.tool_calls.length})</Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                            {agentResult.tool_calls.map((call, idx) => (
                              <Box key={idx} sx={{ background: '#e8eaf6', borderRadius: 1, px: 2, py: 0.5, fontSize: '0.85rem', color: '#667eea', fontWeight: 500 }}>
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
            </Grid>

            {/* Existing Workflow Demo Section */}
            <Grid item xs={12} sm={6}>
              <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderLeft: '4px solid #764ba2', height: '100%' }}>
                <CardContent>
                  <Typography variant="h5" fontWeight={600} gutterBottom>Run Workflow</Typography>
                  <Box component="form" onSubmit={handleSubmit} sx={{ display: 'grid', gap: 2 }}>
                    <Button variant="contained" component="label" sx={{ mb: 1 }}>
                      Upload Workflow YAML
                      <input type="file" accept=".yaml,.yml" hidden onChange={e => setWorkflowFile(e.target.files[0])} required />
                    </Button>
                    <Button variant="contained" component="label" sx={{ mb: 1 }}>
                      Upload Input JSON
                      <input type="file" accept=".json" hidden onChange={e => setInputFile(e.target.files[0])} required />
                    </Button>
                    <FormControl fullWidth sx={{ mb: 1 }}>
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
                    <Button type="submit" variant="contained" color="primary" disabled={loading} sx={{ fontWeight: 600, fontSize: '1rem', py: 1.2 }}>
                      {loading ? <CircularProgress size={24} color="inherit" /> : 'Run Workflow'}
                    </Button>
                  </Box>
                  {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
                </CardContent>
              </Card>
            </Grid>

            {result && (
              <>
                <Grid item xs={12} sm={6}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" fontWeight={600}>Result</Typography>
                      <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>{JSON.stringify(result.result, null, 2)}</Box>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" fontWeight={600}>Tool Results</Typography>
                      <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>{JSON.stringify(result.tool_results, null, 2)}</Box>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12}>
                  <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2 }}>
                    <CardContent>
                      <Typography variant="h6" fontWeight={600}>Audit Log</Typography>
                      <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>{JSON.stringify(result.audit_log, null, 2)}</Box>
                    </CardContent>
                  </Card>
                </Grid>
              </>
            )}
          </Grid>
        </Container>
      </div>
    </div>
  );
}

export default App;
