

import React, { useState } from 'react';
import { Container, Box, Typography, Card, CardContent, Button, TextField, Select, MenuItem, InputLabel, FormControl, Alert, CircularProgress, Grid } from '@mui/material';

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
      const response = await fetch('http://localhost:8002/run-workflow/', {
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
      const response = await fetch('http://localhost:8002/run-ocr/', {
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

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(120deg,#f5f7fa,#c3cfe2)', py: 4, fontFamily: 'Inter, sans-serif' }}>
      <Container maxWidth="sm">
        <Typography variant="h3" align="center" fontWeight={700} color="#222" gutterBottom>
          Agentic Platform Demo UI
        </Typography>

        {/* OCR Demo Section */}
        <Card sx={{ my: 3 }}>
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
        {/* Existing Workflow Demo Section */}
        <Card sx={{ my: 3 }}>
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
        {result && (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight={600}>Result</Typography>
                  <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '1rem', overflowX: 'auto' }}>{JSON.stringify(result.result, null, 2)}</Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight={600}>Tool Results</Typography>
                  <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '1rem', overflowX: 'auto' }}>{JSON.stringify(result.tool_results, null, 2)}</Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight={600}>Audit Log</Typography>
                  <Box component="pre" sx={{ background: '#f6f8fa', borderRadius: 2, p: 2, fontSize: '1rem', overflowX: 'auto' }}>{JSON.stringify(result.audit_log, null, 2)}</Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Container>
    </Box>
  );
}

export default App;
