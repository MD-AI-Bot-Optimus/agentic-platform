import yaml
from typing import Any, Dict

def parse_workflow_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    # Minimal validation
    if "nodes" not in data or "edges" not in data:
        raise ValueError("Invalid workflow YAML: missing nodes or edges")
    return data
