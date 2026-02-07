# ADR-013: LangGraph for Stateful Autonomous Agents

## Context
Up until now, the Agentic Platform relied on a static "Workflow Engine" (deterministic DAG). While robust for predictable processes (OCR), it lacks the flexibility to solve open-ended problems where the next step isn't known in advance.

To support "Agentic Behaviors" (Reasoning loops, Tool use, Memory), we needed a framework that supports:
1.  **Cyclic Graphs:** Loops (Reason &rarr; Act &rarr; Observe &rarr; Reason).
2.  **State Persistence:** Checkpointing the agent's memory (chat history, tool outputs) at every step.
3.  **Human-in-the-Loop:** Pausing execution for approval.

## Decision
We have adopted **LangGraph** (from LangChain) as the engine for our "Agent" tab.

### The Model: ReAct Loop
We implement a **ReAct (Reason + Act)** loop pattern:
1.  **Node: `agent`**: Calls the LLM with the current state + tool descriptions. LLM decides to stop or call a tool.
2.  **Node: `tools`**: Executes the tool requested by the LLM.
3.  **Edge:** Conditional logic loops back to `agent` with the tool output.

### key Components
*   `src/agentic_platform/adapters/langgraph_agent.py`: The main entry point that constructs the graph.
*   `src/agentic_platform/adapters/langgraph_memory.py`: Handles state persistence (checkpointers).

## Consequences
### Positive
*   **observability:** Every step is a "node" in a graph, making it easy to visualize execution traces (which powers our frontend timeline).
*   **Statefulness:** Enables multi-turn conversations and "memory" of past tool results.

### Negative
*   **Complexity:** Graph definitions are more complex than linear chains.
*   **Latency:** Each step involves a full state checkpoint, adding overhead compared to raw API calls.
