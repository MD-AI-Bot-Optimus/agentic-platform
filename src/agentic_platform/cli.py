import argparse
import json
import yaml
from agentic_platform.workflow import engine
from agentic_platform.audit.audit_log import InMemoryAuditLog
from agentic_platform.adapters.mcp_adapter import MCPAdapter

def main():
    parser = argparse.ArgumentParser(description="Run a workflow definition with input artifact.")
    parser.add_argument("--workflow", required=True, help="Path to workflow YAML definition")
    parser.add_argument("--input", required=True, help="Path to input artifact JSON")
    args = parser.parse_args()

    with open(args.workflow, "r") as wf_file:
        wf_def = yaml.safe_load(wf_file)
    with open(args.input, "r") as in_file:
        input_artifact = json.load(in_file)

    audit_log = InMemoryAuditLog()
    tool_client = MCPAdapter()
    result = engine.run(wf_def, input_artifact=input_artifact, tool_client=tool_client, audit_log=audit_log)
    print("Workflow result:")
    print(json.dumps(result, indent=2))
    print("\nAudit log:")
    for event in audit_log.get_events("job-1"):
        print(vars(event))

if __name__ == "__main__":
    main()
