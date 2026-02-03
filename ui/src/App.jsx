import React, { useState } from 'react';
import { Container, Typography, Button, Card, CardContent, Box, Alert, CircularProgress, FormControl, InputLabel, Select, MenuItem, TextField } from '@mui/material';

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

// API Base URL - Use environment variable or default to localhost for dev
const API_BASE_URL = (typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) || (
  typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8003'
    : 'https://agentic-platform-api-170705020917.us-central1.run.app'
);

function App() {
  const [activeView, setActiveView] = useState('workflow');

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

  // Sample data files for quick selection
  const sampleDataFiles = [
    { path: 'sample_data/letter.jpg', name: 'Letter (handwritten)' },
    { path: 'sample_data/handwriting.jpg', name: 'Handwriting Sample' },
    { path: 'sample_data/numbers_gs150.jpg', name: 'Numbers Document' },
    { path: 'sample_data/stock_gs200.jpg', name: 'Stock Image' },
    { path: 'sample_data/ocr_sample_plaid.jpg', name: 'Plaid Pattern' },
    { path: 'sample_data/ocr_sample_image.png', name: 'Sample Image PNG' },
    { path: 'sample_data/ocr_sample_text.png', name: 'Sample Text PNG' },
    { path: 'sample_data/sample_image.png', name: 'Basic Sample' },
  ];

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
      if (!response.ok) throw new Error('API error: ' + response.status);
      setResult(data);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // OCR Handler
  const handleOcrSubmit = async (e) => {
    e.preventDefault();
    setOcrLoading(true);
    setOcrError(null);
    setOcrResult(null);
    const formData = new FormData();

    // Check if it's a sample file (has path property) or uploaded file
    if (ocrImage && ocrImage.path) {
      // Sample file - send file_path as form field
      formData.append('file_path', ocrImage.path);
    } else if (ocrImage) {
      // Uploaded file
      formData.append('image', ocrImage);
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

  return (
    <div style={{
      backgroundColor: '#1a1a2e',
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
          </Box>

          {/* OCR Demo Section */}
          {activeView === 'ocr' && (
            <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #667eea' }}>
              <CardContent>
                <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#667eea' }}>📷 OCR Demonstration</Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Extract text from images using Google Vision API</Typography>

                <Box component="form" onSubmit={handleOcrSubmit} sx={{ display: 'grid', gap: 2 }}>
                  <Box>
                    <Button variant="contained" component="label" sx={{ mb: 1, width: '100%' }}>
                      Upload Image for OCR
                      <input type="file" accept="image/*" hidden onChange={e => setOcrImage(e.target.files[0])} />
                    </Button>
                    {ocrImage && (
                      <Typography variant="body2" sx={{ color: '#4caf50', fontWeight: 500 }}>
                        ✓ Image: {ocrImage.name}
                      </Typography>
                    )}
                  </Box>

                  {/* Sample Files for OCR */}
                  <Box>
                    <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                      📝 Load Sample Image:
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                      {sampleDataFiles.map(file => (
                        <Button
                          key={file.path}
                          variant="outlined"
                          size="small"
                          onClick={() => {
                            // Fetch the sample image file from backend
                            fetch(`${API_BASE_URL}/${file.path}`)
                              .then(res => res.blob())
                              .then(blob => {
                                const imageFile = new File([blob], file.name, { type: blob.type });
                                setOcrImage(imageFile);
                              })
                              .catch(err => {
                                console.error(`Failed to load ${file.name}:`, err);
                                setOcrError(`Failed to load ${file.name}`);
                              });
                          }}
                          sx={{
                            textTransform: 'none',
                            fontSize: '0.85rem',
                            py: 0.8,
                            justifyContent: 'flex-start',
                            color: '#667eea',
                            borderColor: '#667eea',
                            backgroundColor: ocrImage?.name === file.name ? '#e3f2fd' : 'transparent',
                            '&:hover': {
                              backgroundColor: '#e3f2fd',
                              borderColor: '#667eea'
                            }
                          }}
                        >
                          {ocrImage?.name === file.name ? '✓ ' : ''}📄 {file.name}
                        </Button>
                      ))}
                    </Box>
                  </Box>

                  <Button type="submit" variant="contained" color="primary" disabled={ocrLoading || !ocrImage} sx={{ fontWeight: 600, fontSize: '1rem', py: 1.2 }}>
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

                  {mcpToolName === 'google_vision_ocr' && (
                    <Box>
                      <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>Sample Images:</Typography>
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
                    <Box sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '0.85rem', fontFamily: 'monospace', overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
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
                <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#43e97b' }}>⚙️ Run Workflow</Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>Upload workflow YAML and input JSON to execute</Typography>

                <Box component="form" onSubmit={handleSubmit} sx={{ display: 'grid', gap: 2 }}>
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
        </Container>
      </div>
    </div>
  );
}

export default App;
