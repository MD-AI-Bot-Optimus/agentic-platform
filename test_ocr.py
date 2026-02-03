#!/usr/bin/env python3
import yaml
from src.agentic_platform.workflow import engine
from src.agentic_platform.tools.tool_registry import ToolRegistry
from src.agentic_platform.audit.audit_log import InMemoryAuditLog

# Load workflow
with open('src/workflows/ocr_mvp.yaml', 'r') as f:
    wf_def = yaml.safe_load(f)
print('Workflow loaded')

# Test input
input_data = {'image_path': 'sample_data/letter.jpg', 'credentials_json': ''}

# Execute
audit_log = InMemoryAuditLog()
tool_client = ToolRegistry()
result = engine.run(wf_def, input_artifact=input_data, tool_client=tool_client, audit_log=audit_log)
print('Status:', result.get('status'))
if result.get('tool_results'):
    tool_result = result['tool_results'][0]
    if 'result' in tool_result and 'text' in tool_result['result']:
        text = tool_result['result']['text']
        print('Text length:', len(text))
        print('First 100 chars:', text[:100])
    else:
        print('No text in result')
        print('Tool result keys:', list(tool_result.keys()))
        if 'result' in tool_result:
            print('Result keys:', list(tool_result['result'].keys()))
else:
    print('No tool results')
    print('Result keys:', list(result.keys()))