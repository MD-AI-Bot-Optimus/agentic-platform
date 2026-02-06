#!/usr/bin/env python
"""
LangGraph Agent Demo
====================

Demonstrates autonomous agent reasoning with multiple reasoning steps,
tool execution, and memory management.

This demo shows:
1. Agent initialization with multiple tools
2. Multi-step reasoning process
3. Tool execution decisions
4. Memory retention across steps
5. Final output generation
"""

import sys
from typing import Optional
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, "/Users/manishdube/Documents/src")

from agentic_platform.adapters.langgraph_agent import LangGraphAgent
from agentic_platform.adapters.langgraph_tools import ToolRegistry, ToolBinding
from agentic_platform.adapters.langgraph_memory import InMemoryMemory
from agentic_platform.llm.mock_llm import MockLLM
from langchain_core.tools import StructuredTool


# ============================================================================
# Sample Tools for Demo
# ============================================================================

class DocumentProcessingTools:
    """Sample tools for document processing workflow."""
    
    @staticmethod
    def extract_text(image_path: str) -> dict:
        """Extract text from an image using OCR."""
        print(f"  [TOOL EXECUTION] extract_text: Processing {image_path}")
        
        # Simulate OCR results
        if "invoice" in image_path.lower():
            return {
                "text": "INVOICE #12345\nDate: 2024-01-15\nAmount: $1,500.00\nClient: Acme Corp",
                "confidence": 0.98,
                "symbols_count": 450
            }
        elif "contract" in image_path.lower():
            return {
                "text": "AGREEMENT DOCUMENT\nParties: Company A and Company B\nEffective Date: Jan 1, 2024\nTerm: 2 years",
                "confidence": 0.95,
                "symbols_count": 320
            }
        else:
            return {
                "text": "Sample text from document",
                "confidence": 0.92,
                "symbols_count": 200
            }
    
    @staticmethod
    def analyze_sentiment(text: str) -> dict:
        """Analyze sentiment of extracted text."""
        print(f"  [TOOL EXECUTION] analyze_sentiment: Analyzing {len(text)} chars")
        
        # Simple sentiment simulation
        if any(word in text.lower() for word in ["agreement", "confirmed", "approved"]):
            sentiment = "positive"
            score = 0.85
        elif any(word in text.lower() for word in ["error", "issue", "problem"]):
            sentiment = "negative"
            score = 0.75
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "summary": f"Text has {sentiment} sentiment"
        }
    
    @staticmethod
    def classify_document(text: str) -> dict:
        """Classify document type."""
        print(f"  [TOOL EXECUTION] classify_document: Classifying document")
        
        text_lower = text.lower()
        
        if "invoice" in text_lower:
            doc_type = "INVOICE"
        elif "agreement" in text_lower or "contract" in text_lower:
            doc_type = "CONTRACT"
        elif "purchase" in text_lower or "order" in text_lower:
            doc_type = "PURCHASE_ORDER"
        else:
            doc_type = "GENERIC_DOCUMENT"
        
        return {
            "type": doc_type,
            "confidence": 0.88,
            "category": "business_document"
        }
    
    @staticmethod
    def summary_with_facts(text: str) -> dict:
        """Extract key facts from document."""
        print(f"  [TOOL EXECUTION] summary_with_facts: Extracting facts")
        
        sentences = text.split('\n')
        facts = [s.strip() for s in sentences if s.strip()][:3]
        
        return {
            "key_facts": facts,
            "fact_count": len(facts),
            "summary": "Key information extracted successfully"
        }


# ============================================================================
# Demo Execution
# ============================================================================

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n  ► {title}")
    print("  " + "-" * 76)


def demo_basic_reasoning():
    """Demo 1: Basic agent reasoning."""
    print_section("DEMO 1: Basic Agent Reasoning")
    
    # Initialize agent
    print_subsection("Initializing Agent")
    llm = MockLLM()
    agent = LangGraphAgent(
        model="mock-llm",
        llm=llm,
        max_iterations=3
    )
    print(f"  ✓ Agent initialized with MockLLM")
    print(f"  ✓ Max iterations: {agent.max_iterations}")
    
    # Execute simple query
    print_subsection("Executing Query: 'What is artificial intelligence?'")
    result = agent.execute("What is artificial intelligence?")
    
    # Display results
    print(f"  Status: {result.status}")
    print(f"  Iterations: {result.iterations}")
    print(f"  Reasoning Steps: {len(result.reasoning_steps)}")
    for i, step in enumerate(result.reasoning_steps, 1):
        print(f"    Step {i}: {step[:60]}...")


def demo_with_tools():
    """Demo 2: Agent with tools."""
    print_section("DEMO 2: Agent with Document Processing Tools")
    
    # Initialize agent
    print_subsection("Setting up Agent with Tools")
    llm = MockLLM()
    agent = LangGraphAgent(
        model="mock-llm",
        llm=llm,
        max_iterations=5
    )
    print(f"  ✓ Agent initialized")
    
    # Create tools
    print_subsection("Registering Tools")
    tools = ToolRegistry()
    
    tools.register(
        "extract_text",
        DocumentProcessingTools.extract_text,
        {"image_path": {"type": str, "description": "Path to image file"}}
    )
    print(f"  ✓ Registered: extract_text")
    
    tools.register(
        "analyze_sentiment",
        DocumentProcessingTools.analyze_sentiment,
        {"text": {"type": str, "description": "Text to analyze"}}
    )
    print(f"  ✓ Registered: analyze_sentiment")
    
    tools.register(
        "classify_document",
        DocumentProcessingTools.classify_document,
        {"text": {"type": str, "description": "Document text"}}
    )
    print(f"  ✓ Registered: classify_document")
    
    # Add tools to agent
    agent.with_tools(tools.get_all())
    print(f"  ✓ Agent has {len(agent.tools)} tools available")
    
    # Execute query
    print_subsection("Executing Query: 'Process invoice.pdf'")
    result = agent.execute("Process invoice.pdf - extract text and classify it")
    
    # Display results
    print(f"\n  Status: {result.status}")
    print(f"  Iterations: {result.iterations}")
    print(f"  Tool Calls: {len(result.tool_calls)}")
    
    for i, call in enumerate(result.tool_calls, 1):
        print(f"    Tool {i}: {call['tool']}")
        if 'result' in call:
            print(f"      Result: {str(call['result'])[:50]}...")


def demo_memory_management():
    """Demo 3: Memory management."""
    print_section("DEMO 3: Memory Management")
    
    # Initialize with custom memory
    print_subsection("Setting up Agent with Custom Memory")
    llm = MockLLM()
    memory = InMemoryMemory(max_entries=10)
    agent = LangGraphAgent(
        model="mock-llm",
        llm=llm,
        memory=memory,
        max_iterations=3
    )
    print(f"  ✓ Agent initialized with InMemoryMemory (max {memory.max_entries} entries)")
    
    # Multiple executions
    print_subsection("Executing Multiple Queries")
    queries = [
        "Hello, what's your name?",
        "Tell me about Python",
        "What did I ask you earlier?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n  Query {i}: {query}")
        result = agent.execute(query)
        print(f"  Response iterations: {result.iterations}")
        print(f"  Total memory entries: {len(memory)}")
    
    # Display memory
    print_subsection("Memory Context")
    context = memory.get_context(5)
    print(f"\n  {context}")


def demo_multi_step_workflow():
    """Demo 4: Multi-step document processing workflow."""
    print_section("DEMO 4: Multi-Step Document Workflow")
    
    # Initialize
    print_subsection("Setting up Multi-Step Workflow")
    llm = MockLLM()
    agent = LangGraphAgent(
        model="mock-llm",
        llm=llm,
        max_iterations=6
    )
    
    # Setup tools
    tools = ToolRegistry()
    tools.register(
        "extract_text",
        DocumentProcessingTools.extract_text,
        {"image_path": {"type": str, "description": "Path to image"}}
    )
    tools.register(
        "analyze_sentiment",
        DocumentProcessingTools.analyze_sentiment,
        {"text": {"type": str, "description": "Text to analyze"}}
    )
    tools.register(
        "classify_document",
        DocumentProcessingTools.classify_document,
        {"text": {"type": str, "description": "Document text"}}
    )
    tools.register(
        "summary_with_facts",
        DocumentProcessingTools.summary_with_facts,
        {"text": {"type": str, "description": "Document text"}}
    )
    
    agent.with_tools(tools.get_all())
    print(f"  ✓ Agent ready with {len(agent.tools)} document processing tools")
    
    # Execute complex workflow
    print_subsection("Executing: 'Process contract.pdf and provide analysis'")
    result = agent.execute(
        "Please process contract.pdf: extract text, classify it, analyze sentiment, and provide key facts"
    )
    
    # Display full workflow
    print(f"\n  Status: {result.status}")
    print(f"  Total Iterations: {result.iterations}")
    print(f"  Reasoning Steps: {len(result.reasoning_steps)}")
    print(f"  Tool Calls Made: {len(result.tool_calls)}")
    
    print("\n  Reasoning Process:")
    for i, step in enumerate(result.reasoning_steps, 1):
        step_text = step[:70] + "..." if len(step) > 70 else step
        print(f"    {i}. {step_text}")
    
    print("\n  Tool Execution Sequence:")
    for i, call in enumerate(result.tool_calls, 1):
        print(f"    {i}. {call['tool']} call")


def demo_agent_reset():
    """Demo 5: Agent state management."""
    print_section("DEMO 5: Agent State Management")
    
    # Initialize
    print_subsection("Testing Agent Reset")
    llm = MockLLM()
    agent = LangGraphAgent(model="mock-llm", llm=llm, max_iterations=2)
    
    # First execution
    print("  Execution 1:")
    result1 = agent.execute("First query")
    print(f"    Reasoning steps: {len(agent.reasoning_steps)}")
    print(f"    Memory entries: {len(agent.memory)}")
    
    # Reset agent
    print("\n  Resetting agent...")
    agent.reset()
    print(f"    Reasoning steps after reset: {len(agent.reasoning_steps)}")
    print(f"    Memory entries after reset: {len(agent.memory)}")
    
    # Second execution (fresh state)
    print("\n  Execution 2 (after reset):")
    result2 = agent.execute("Second query")
    print(f"    Reasoning steps: {len(agent.reasoning_steps)}")
    print(f"    Memory entries: {len(agent.memory)}")


# ============================================================================
# Main Demo Runner
# ============================================================================

def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " LANGGRAPH AGENT DEMONSTRATION ".center(78) + "║")
    print("║" + " Autonomous Reasoning with Tool Integration ".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Run demos
        demo_basic_reasoning()
        demo_with_tools()
        demo_memory_management()
        demo_multi_step_workflow()
        demo_agent_reset()
        
        # Summary
        print_section("DEMO COMPLETE")
        print("""
  ✓ Basic reasoning demonstrated
  ✓ Tool integration working
  ✓ Memory management functional
  ✓ Multi-step workflows executed
  ✓ State management verified
  
  Key Capabilities Shown:
  • Autonomous reasoning loop
  • Tool selection and execution
  • Conversation memory with context
  • Multi-iteration problem solving
  • State reset and cleanup
        """)
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
