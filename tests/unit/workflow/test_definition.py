import pytest
from agentic_platform.workflow import definition
import tempfile
import yaml

def test_parse_workflow_definition_from_yaml():
    yaml_content = """
    nodes:
      - id: start
        type: start
      - id: ocr
        type: tool
        tool: ocr_page
      - id: end
        type: end
    edges:
      - from: start
        to: ocr
      - from: ocr
        to: end
    """
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        wf = definition.parse_workflow_yaml(f.name)
    assert "nodes" in wf
    assert "edges" in wf
    assert wf["nodes"][0]["id"] == "start"
    assert wf["edges"][0]["from"] == "start"
