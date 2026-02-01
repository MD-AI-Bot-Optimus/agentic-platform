# ADR-005: Model Selection Per Node/Task

## Status
Accepted

## Context
Different workflow nodes or tasks may require different LLMs or tool models (e.g., GPT-4 for summarization, OCR model for extraction). The platform must support explicit model selection per node/task.

## Decision
A ModelRouter utility is introduced to route tool calls to the specified model for each node/task. The workflow definition can specify the model to use, and ModelRouter enforces this at runtime.

## Consequences
- Enables fine-grained control over model/tool selection.
- Supports fallback/default model logic.
- Model selection logic is isolated from core workflow engine.

## Related Milestones
- ModelRouter implementation (2026-01-25)
- Per-node model selection tests (2026-01-25)
