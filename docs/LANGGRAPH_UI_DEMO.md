# LangGraph Agent UI Demo Guide

Show the LangGraph agent working in real-time through the UI, visualizing routing, tool execution, and message accumulation like the OCR demo.

---

## Overview

The current UI has:
- ✅ **OCR Demo** - Calls `/run-ocr/` endpoint, shows extracted text
- ✅ **MCP Tool Tester** - Calls tools via JSON-RPC
- 🔴 **Missing: LangGraph Agent Demo** - Show agent reasoning, routing, and multi-step execution

---

## Architecture: How to Add LangGraph Agent to UI

### Step 1: Create API Endpoint for Agent Execution

**File**: `src/agentic_platform/api.py`

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agentic_platform.adapters.langgraph_agent import LangGraphAgent, AgentExecutionResult

app = FastAPI()

# Define request/response models
class AgentExecuteRequest(BaseModel):
    prompt: str
    model: str = "mock-llm"
    max_iterations: int = 10
    tools: list = []  # Optional: ["ocr", "search", etc.]

class ExecutionStep(BaseModel):
    step_number: int
    node_type: str  # "agent", "tool", "router"
    message: str
    reasoning: str = ""
    tool_name: str = ""
    tool_input: dict = {}
    tool_result: str = ""

class AgentExecuteResponse(BaseModel):
    status: str  # "success", "incomplete", "error"
    final_output: str
    reasoning_steps: list[str]
    tool_calls: list[dict]
    iterations: int
    execution_trace: list[ExecutionStep]  # ← NEW: For UI visualization
    error: str = ""

@app.post("/agent/execute", response_model=AgentExecuteResponse)
async def execute_agent(request: AgentExecuteRequest):
    """
    Execute LangGraph agent with execution tracing.
    
    Returns execution trace so UI can show each step.
    """
    try:
        llm = get_llm_model(provider=request.model)
        agent = LangGraphAgent(llm=llm, max_iterations=request.max_iterations)
        
        # Execute with tracing
        result = agent.execute(request.prompt)
        
        # Build execution trace for UI
        execution_trace = build_execution_trace(agent, result)
        
        return AgentExecuteResponse(
            status=result.status,
            final_output=str(result.final_output),
            reasoning_steps=result.reasoning_steps,
            tool_calls=result.tool_calls,
            iterations=result.iterations,
            execution_trace=execution_trace,
            error=result.error or ""
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def build_execution_trace(agent, result):
    """Build step-by-step execution trace from agent state."""
    trace = []
    step_num = 1
    
    # Reconstruct steps from reasoning_steps and tool_calls
    for i, reasoning_step in enumerate(result.reasoning_steps):
        trace.append(ExecutionStep(
            step_number=step_num,
            node_type="agent",
            message=f"Iteration {i+1}: Reasoning",
            reasoning=reasoning_step
        ))
        step_num += 1
    
    for tool_call in result.tool_calls:
        trace.append(ExecutionStep(
            step_number=step_num,
            node_type="tool",
            message=f"Executing tool: {tool_call.get('tool', 'unknown')}",
            tool_name=tool_call.get("tool", ""),
            tool_input=tool_call.get("input", {}),
            tool_result=tool_call.get("result", "")
        ))
        step_num += 1
    
    return trace
```

---

### Step 2: Add Agent Demo Tab to UI

**File**: `ui/src/App.jsx`

Add to state section:

```jsx
// LangGraph Agent state
const [agentPrompt, setAgentPrompt] = useState('What is artificial intelligence?');
const [agentModel, setAgentModel] = useState('mock-llm');
const [agentMaxIterations, setAgentMaxIterations] = useState(10);
const [agentResult, setAgentResult] = useState(null);
const [agentLoading, setAgentLoading] = useState(false);
const [agentError, setAgentError] = useState(null);
const [expandedStep, setExpandedStep] = useState(null);
```

Add handler function:

```jsx
// Agent Handler
const handleAgentSubmit = async (e) => {
  e.preventDefault();
  setAgentLoading(true);
  setAgentError(null);
  setAgentResult(null);

  try {
    const response = await fetch(`${API_BASE_URL}/agent/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: agentPrompt,
        model: agentModel,
        max_iterations: agentMaxIterations,
      }),
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
```

Add tab button to navigation:

```jsx
<Button 
  onClick={() => setActiveView('agent')}
  sx={{
    color: activeView === 'agent' ? '#667eea' : '#666',
    fontWeight: activeView === 'agent' ? 700 : 500,
  }}
>
  🤖 LangGraph Agent
</Button>
```

Add Agent Demo section:

```jsx
{/* LangGraph Agent Demo Section */}
{activeView === 'agent' && (
  <Card sx={{ background: '#ffffff', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', borderRadius: 2, borderTop: '4px solid #667eea' }}>
    <CardContent>
      <Typography variant="h5" fontWeight={700} gutterBottom sx={{ color: '#667eea' }}>
        🤖 LangGraph Agent Reasoning
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Watch the agent reason, route decisions, and execute tools in real-time
      </Typography>

      <Box component="form" onSubmit={handleAgentSubmit} sx={{ display: 'grid', gap: 2 }}>
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

        <TextField
          label="Max Iterations"
          type="number"
          value={agentMaxIterations}
          onChange={(e) => setAgentMaxIterations(parseInt(e.target.value))}
          disabled={agentLoading}
          inputProps={{ min: 1, max: 20 }}
        />

        <Button 
          type="submit" 
          variant="contained" 
          color="primary" 
          disabled={agentLoading}
          sx={{ fontWeight: 600, fontSize: '1rem', py: 1.2 }}
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
              Status: <span style={{ textTransform: 'uppercase' }}>{agentResult.status}</span>
            </Typography>
            <Typography variant="body2">
              Iterations: {agentResult.iterations} | Tool Calls: {agentResult.tool_calls.length}
            </Typography>
          </Box>

          {/* Execution Steps Timeline */}
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>⏱️ Execution Timeline</Typography>
          <Box sx={{ 
            border: '1px solid #e0e0e0',
            borderRadius: 1,
            overflow: 'hidden'
          }}>
            {agentResult.execution_trace.map((step, idx) => (
              <Box key={idx}>
                <Box
                  onClick={() => setExpandedStep(expandedStep === idx ? null : idx)}
                  sx={{
                    background: step.node_type === 'agent' ? '#f5f5f5' : step.node_type === 'tool' ? '#fff9e6' : '#e8f5e9',
                    p: 2,
                    borderBottom: '1px solid #e0e0e0',
                    cursor: 'pointer',
                    '&:hover': { background: step.node_type === 'agent' ? '#f0f0f0' : step.node_type === 'tool' ? '#fff8e0' : '#e8f5e0' },
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Step {step.step_number}: {
                        step.node_type === 'agent' ? '🧠 Agent Reasoning' :
                        step.node_type === 'tool' ? '🔧 Tool Execution' :
                        '🚦 Router Decision'
                      }
                    </Typography>
                    <Typography variant="body2" color="textSecondary">{step.message}</Typography>
                  </Box>
                  <Typography sx={{ color: '#999', ml: 2 }}>
                    {expandedStep === idx ? '▼' : '▶'}
                  </Typography>
                </Box>

                {/* Expanded Details */}
                {expandedStep === idx && (
                  <Box sx={{ background: '#f9f9f9', p: 2, borderBottom: '1px solid #e0e0e0' }}>
                    {step.reasoning && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Reasoning:</Typography>
                        <Box sx={{ background: '#fff', p: 1.5, borderRadius: 1, fontSize: '0.85rem', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                          {step.reasoning}
                        </Box>
                      </Box>
                    )}
                    {step.tool_name && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Tool: {step.tool_name}</Typography>
                        <Box sx={{ background: '#fff', p: 1.5, borderRadius: 1 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>Input:</Typography>
                          <pre style={{ fontSize: '0.75rem', overflow: 'auto' }}>
                            {JSON.stringify(step.tool_input, null, 2)}
                          </pre>
                          {step.tool_result && (
                            <>
                              <Typography variant="body2" sx={{ fontWeight: 600, mt: 1 }}>Result:</Typography>
                              <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: '200px' }}>
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
            ))}
          </Box>

          {/* Final Output */}
          <Typography variant="h6" sx={{ fontWeight: 600, mt: 3, mb: 1 }}>✅ Final Output</Typography>
          <Box sx={{ background: '#f6f8fa', borderRadius: 1, p: 2, fontSize: '0.95rem', whiteSpace: 'pre-wrap' }}>
            {agentResult.final_output}
          </Box>

          {/* Reasoning Steps */}
          <Typography variant="h6" sx={{ fontWeight: 600, mt: 3, mb: 1 }}>📝 All Reasoning Steps</Typography>
          <Box sx={{ background: '#f6f8fa', borderRadius: 1, p: 2 }}>
            {agentResult.reasoning_steps.map((step, idx) => (
              <Box key={idx} sx={{ mb: 1.5, pb: 1.5, borderBottom: idx < agentResult.reasoning_steps.length - 1 ? '1px solid #ddd' : 'none' }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#667eea' }}>Step {idx + 1}:</Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>{step}</Typography>
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </CardContent>
  </Card>
)}
```

---

## Step 3: Real-Time Message Visualization (Advanced)

For seeing messages accumulate in real-time, add streaming capability:

```jsx
const handleAgentStreamSubmit = async (e) => {
  e.preventDefault();
  setAgentLoading(true);
  setAgentError(null);
  setAgentResult(null);

  try {
    const response = await fetch(`${API_BASE_URL}/agent/execute-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: agentPrompt,
        model: agentModel,
        max_iterations: agentMaxIterations,
      }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullResult = { execution_trace: [] };

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.step) {
              // Add step to display in real-time
              setAgentResult(prev => ({
                ...prev,
                execution_trace: [...(prev?.execution_trace || []), data.step]
              }));
            }
          } catch (e) {
            console.error('Failed to parse stream:', e);
          }
        }
      }
    }

    // Get final result
    const finalData = await response.json();
    setAgentResult(finalData);
  } catch (err) {
    setAgentError(err.message);
  } finally {
    setAgentLoading(false);
  }
};
```

---

## Step 4: API Endpoint for Streaming

**File**: `src/agentic_platform/api.py`

```python
from fastapi.responses import StreamingResponse

@app.post("/agent/execute-stream")
async def execute_agent_stream(request: AgentExecuteRequest):
    """
    Stream agent execution steps in real-time.
    Sends Server-Sent Events (SSE) with each step.
    """
    async def generate():
        try:
            llm = get_llm_model(provider=request.model)
            agent = LangGraphAgent(llm=llm, max_iterations=request.max_iterations)
            
            # Hook into agent state updates
            step_num = 1
            
            # Execute with callbacks
            result = await agent.execute_with_callbacks(
                request.prompt,
                on_step=lambda step: generate_step_event(step, step_num)
            )
            
            # Send final result
            yield f"data: {json.dumps({'final': True, 'result': result})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

def generate_step_event(step_data, step_num):
    """Generate SSE event for a step."""
    return f"data: {json.dumps({'step': {**step_data, 'step_number': step_num}})}\n\n"
```

---

## Visualization Features

### 1. **Message Flow Diagram**
```
User Input
    ↓
🧠 Agent Node (Reasoning)
    ↓
🚦 Router (Decision)
    ↙         ↘
  Tool?     Final?
    ↓         ↓
🔧 Tool Node ✅ END
    ↓
📝 Message added to state
    ↓
🧠 Agent Node (Next iteration)
```

### 2. **State Accumulation Display**
```
Messages Accumulated:
[1] Human: "What is AI?"
[2] AI: "I need to search for information. use_tool: search_ai"
[3] Tool: Search returned 5 results
[4] AI: "Based on the search results, AI is..."
[5] ✅ Final answer (no tool needed)
```

### 3. **Tool Execution Timeline**
```
Step 1: 🧠 Agent Reasoning
  └─ Decided to use: search tool

Step 2: 🔧 Tool Execution
  ├─ Tool: search
  ├─ Input: { query: "artificial intelligence" }
  └─ Result: 5 matching articles

Step 3: 🧠 Agent Reasoning
  └─ Processed tool result, generating answer
```

---

## Testing the UI Demo

### Run Backend:
```bash
cd /Users/manishdube/Documents/src/agentic-platform

# Start API
python -m uvicorn src.agentic_platform.api:app --reload --port 8000
```

### Run Frontend:
```bash
cd ui
npm run dev
```

### Access:
- Open `http://localhost:5173`
- Click "🤖 LangGraph Agent" tab
- Enter prompt, select model, click "Execute Agent"
- Watch reasoning steps and tool execution in real-time

---

## What You'll See

### Without Tools:
```
Prompt: "What is artificial intelligence?"

Step 1: 🧠 Agent Reasoning
  └─ No tools needed, generating direct answer

✅ Final Output:
   "Artificial intelligence (AI) refers to..."
```

### With Tools:
```
Prompt: "Search for latest AI news and summarize"

Step 1: 🧠 Agent Reasoning
  └─ Reasoning: "Need to search for latest AI news"

Step 2: 🚦 Router Decision
  └─ Route: "tool_node" (tool use detected)

Step 3: 🔧 Tool Execution
  ├─ Tool: search
  ├─ Input: { query: "latest AI news 2026" }
  └─ Result: 10 articles found

Step 4: 🧠 Agent Reasoning (Iteration 2)
  └─ Reasoning: "Processing search results..."

Step 5: 🚦 Router Decision
  └─ Route: "__end__" (sufficient info, no more tools)

✅ Final Output:
   "Here's a summary of latest AI news..."
```

---

## Benefits Over Current Setup

| Aspect | Current (OCR Only) | With LangGraph Agent |
|--------|---|---|
| **Visible Steps** | 1 (OCR extraction) | 5-10 (reasoning, routing, tool execution) |
| **Routing Logic** | N/A | See live router decisions |
| **Message Flow** | Input → Output | Full conversation history accumulation |
| **Tool Chains** | Single tool | Multi-step tool use |
| **Debugging** | Binary (pass/fail) | See each iteration with details |

---

## Next Steps

1. ✅ Create `/agent/execute` endpoint
2. ✅ Add Agent tab to UI with form inputs
3. ✅ Display execution timeline with expandable steps
4. ✅ Show final output and reasoning steps
5. 🔲 Add streaming support for real-time visualization
6. 🔲 Add graph visualization (show state machine)
7. 🔲 Add message history panel
8. 🔲 Add tool call inspector

