"""
Agent Memory Management

Handles conversation history, context preservation, and memory operations.
Supports multiple backends: in-memory, SQLite (future).
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Single memory entry."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class MemoryManager:
    """Base memory manager."""
    
    def __init__(self):
        self.entries: List[MemoryEntry] = []
    
    def add(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add entry to memory."""
        entry = MemoryEntry(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        self.entries.append(entry)
        logger.debug(f"Added {role} message to memory (total: {len(self.entries)})")
    
    def add_human(self, content: str) -> None:
        """Add human message."""
        self.add("user", content)
    
    def add_assistant(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add assistant message."""
        self.add("assistant", content, metadata)
    
    def add_tool_result(self, tool_name: str, result: Any) -> None:
        """Add tool result to memory."""
        self.add("tool", f"{tool_name}: {str(result)}", {"tool": tool_name})
    
    def get_recent(self, n: int = 5) -> List[MemoryEntry]:
        """Get recent n entries."""
        return self.entries[-n:]
    
    def get_context(self, n: int = 10) -> str:
        """Get context from recent messages for prompt injection."""
        recent = self.get_recent(n)
        context_parts = []
        for entry in recent:
            context_parts.append(f"{entry.role}: {entry.content}")
        return "\n".join(context_parts)
    
    def to_langchain_messages(self) -> List[BaseMessage]:
        """Convert to LangChain message format."""
        messages = []
        for entry in self.entries:
            if entry.role == "user":
                messages.append(HumanMessage(content=entry.content))
            elif entry.role == "assistant":
                messages.append(AIMessage(content=entry.content))
        return messages
    
    def clear(self) -> None:
        """Clear all memory."""
        self.entries = []
        logger.info("Memory cleared")
    
    def __len__(self) -> int:
        """Number of entries."""
        return len(self.entries)
    
    def __str__(self) -> str:
        """String representation."""
        return f"MemoryManager({len(self.entries)} entries)"


class InMemoryMemory(MemoryManager):
    """In-memory message storage."""
    
    def __init__(self, max_entries: int = 100):
        super().__init__()
        self.max_entries = max_entries
    
    def add(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add entry, respecting max_entries limit."""
        super().add(role, content, metadata)
        
        # Remove oldest if exceeding max
        if len(self.entries) > self.max_entries:
            removed = self.entries.pop(0)
            logger.debug(f"Removed oldest entry to stay under {self.max_entries} limit")


class ConversationSummary:
    """Summarize conversation for context efficiency."""
    
    @staticmethod
    def summarize(memory: MemoryManager, llm) -> str:
        """
        Summarize memory entries for efficient context.
        
        Uses LLM to create concise summary of conversation.
        """
        context = memory.get_context(20)  # Get last 20 entries
        
        prompt = f"""Provide a concise summary of this conversation in 2-3 sentences:

{context}

Summary:"""
        
        # Use LLM to summarize
        try:
            response = llm.invoke(prompt)
            summary = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"Generated summary: {summary[:100]}...")
            return summary
        except Exception as e:
            logger.error(f"Failed to summarize: {e}")
            return "Conversation history available"


class MemorySearcher:
    """Search memory for relevant information."""
    
    @staticmethod
    def search_keyword(memory: MemoryManager, keyword: str) -> List[MemoryEntry]:
        """Search memory by keyword."""
        return [e for e in memory.entries if keyword.lower() in e.content.lower()]
    
    @staticmethod
    def search_by_role(memory: MemoryManager, role: str) -> List[MemoryEntry]:
        """Search memory by role."""
        return [e for e in memory.entries if e.role == role]
    
    @staticmethod
    def search_by_time_range(memory: MemoryManager, start_time: str, end_time: str) -> List[MemoryEntry]:
        """Search memory by time range (ISO format)."""
        return [
            e for e in memory.entries 
            if start_time <= e.timestamp <= end_time
        ]


def memory_to_dict(memory: MemoryManager) -> Dict[str, Any]:
    """Convert memory to dictionary for serialization."""
    return {
        "entries": [asdict(e) for e in memory.entries],
        "total_entries": len(memory.entries),
        "created_at": datetime.now().isoformat()
    }


def dict_to_memory(data: Dict[str, Any]) -> MemoryManager:
    """Convert dictionary back to memory."""
    memory = MemoryManager()
    for entry_dict in data.get("entries", []):
        entry = MemoryEntry(**entry_dict)
        memory.entries.append(entry)
    return memory
