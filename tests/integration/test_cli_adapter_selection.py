import subprocess
import sys
import os

def test_cli_adapter_selection():
    cli_path = os.path.join(os.path.dirname(__file__), "../../src/agentic_platform/cli.py")
    workflow_path = os.path.join(os.path.dirname(__file__), "../../demo_workflow.yaml")
    input_path = os.path.join(os.path.dirname(__file__), "../../demo_input.json")

    # Test MCP (default)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
    result = subprocess.run([sys.executable, cli_path, "--workflow", workflow_path, "--input", input_path], capture_output=True, text=True, env=env)
    assert result.returncode == 0
    assert "MCP simulated response" in result.stdout

    # Test LangGraph
    result = subprocess.run([sys.executable, cli_path, "--workflow", workflow_path, "--input", input_path, "--adapter", "langgraph"], capture_output=True, text=True, env=env)
    assert result.returncode == 0
    assert "LangGraph simulated response" in result.stdout
