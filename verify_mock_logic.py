import requests
import json
import sys

def test_mock_logic():
    url = "http://localhost:8003/agent/execute"
    payload = {
        "prompt": "What is a neural network?",
        "model": "gemini-2.0-flash"
    }
    
    print(f"Testing {url} with model {payload['model']}...")
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        
        # Check 1: Multi-step reasoning
        steps = data.get("reasoning_steps", [])
        print(f"\nReasoning Steps ({len(steps)}):")
        for step in steps:
            print(f"- {step}")
            
        if len(steps) < 2:
            print("\n[FAIL] Expected multiple reasoning steps (Plan -> Answer), but got generic response.")
            return False
            
        # Check 2: Tool usage simulation
        has_tool_use = any("use_tool" in step for step in steps)
        if not has_tool_use:
            print("\n[FAIL] Did not detect 'use_tool' in reasoning steps.")
            return False
            
        # Check 3: Persona prefix
        final_output = data.get("final_output", "")
        print(f"\nFinal Output: {final_output[:100]}...")
        
        if "⚡ [Gemini 2.0 Flash]" not in final_output:
            print("\n[FAIL] Final output missing Gemini 2.0 Flash persona prefix.")
            return False
            
        print("\n[SUCCESS] Enhanced Mock Logic Verified!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_mock_logic()
    sys.exit(0 if success else 1)
