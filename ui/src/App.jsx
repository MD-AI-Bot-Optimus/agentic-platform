

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
  const [mcpArgs, setMcpArgs] = useState('{"image_path": "/path/to/image.jpg"}');
  const [mcpResult, setMcpResult] = useState(null);
  const [mcpAvailableTools, setMcpAvailableTools] = useState([]);
  const [mcpLoading, setMcpLoading] = useState(false);
  const [mcpError, setMcpError] = useState(null);

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

                    {/* Arguments Input */}
                    <TextField
                      label="Tool Arguments (JSON)"
                      multiline
                      rows={4}
                      value={mcpArgs}
                      onChange={e => setMcpArgs(e.target.value)}
                      placeholder='{"key": "value"}'
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
