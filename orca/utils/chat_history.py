"""
Chat History Utilities
======================

Conversation history management utilities for LangChain/LangGraph integration.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ChatHistoryHelper:
    """
    Helper class for working with chat history from Orca requests.
    Makes it easy to convert to LangChain message formats.
    
    Usage:
        history = ChatHistoryHelper(data.chat_history)
        
        # Get as LangChain messages
        messages = history.to_langchain_messages()
        
        # Get as simple list
        history_list = history.get_messages()
        
        # Get only user messages
        user_msgs = history.get_user_messages()
        
        # Get last N messages
        recent = history.get_last_n_messages(10)
    """
    
    def __init__(self, chat_history: List[Dict[str, str]]):
        """
        Initialize with chat_history from request.
        
        Args:
            chat_history: List of message dictionaries from ChatMessage.chat_history
        """
        self.history = chat_history or []
    
    def to_langchain_messages(self, include_system: Optional[str] = None) -> List[Any]:
        """
        Convert to LangChain message objects.
        
        Args:
            include_system: Optional system message to prepend
            
        Returns:
            List of LangChain message objects (HumanMessage, AIMessage, SystemMessage)
        """
        try:
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        except ImportError:
            logger.warning("langchain_core not installed. Install with: pip install langchain-core")
            raise ImportError("langchain_core is required for to_langchain_messages(). Install with: pip install langchain-core")
        
        messages = []
        
        if include_system:
            messages.append(SystemMessage(content=include_system))
        
        for msg in self.history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "system":
                messages.append(SystemMessage(content=content))
        
        return messages
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get raw message list.
        
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        return self.history
    
    def get_user_messages(self) -> List[str]:
        """
        Get only user message contents.
        
        Returns:
            List of user message content strings
        """
        return [msg["content"] for msg in self.history if msg.get("role") == "user"]
    
    def get_assistant_messages(self) -> List[str]:
        """
        Get only assistant message contents.
        
        Returns:
            List of assistant message content strings
        """
        return [msg["content"] for msg in self.history if msg.get("role") == "assistant"]
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """
        Get the last N messages.
        
        Args:
            n: Number of messages to retrieve
            
        Returns:
            List of the last N message dictionaries
        """
        return self.history[-n:] if n > 0 else []
    
    def get_last_n_langchain_messages(self, n: int, include_system: Optional[str] = None) -> List[Any]:
        """
        Get the last N messages as LangChain objects.
        
        Args:
            n: Number of messages to retrieve
            include_system: Optional system message to prepend
            
        Returns:
            List of LangChain message objects
        """
        last_n = self.get_last_n_messages(n)
        temp_helper = ChatHistoryHelper(last_n)
        return temp_helper.to_langchain_messages(include_system=include_system)
    
    def count(self) -> int:
        """
        Get total message count.
        
        Returns:
            Number of messages in history
        """
        return len(self.history)
    
    def is_empty(self) -> bool:
        """
        Check if history is empty.
        
        Returns:
            True if history is empty, False otherwise
        """
        return len(self.history) == 0
    
    def get_context_string(self, max_messages: Optional[int] = None) -> str:
        """
        Get history as a formatted string for context.
        
        Args:
            max_messages: Optional limit on number of messages to include
            
        Returns:
            Formatted string with conversation history
        """
        messages = self.history if max_messages is None else self.history[-max_messages:]
        
        lines = []
        for msg in messages:
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def filter_by_role(self, role: str) -> List[Dict[str, str]]:
        """
        Filter messages by role.
        
        Args:
            role: Role to filter by ('user', 'assistant', or 'system')
            
        Returns:
            List of messages matching the specified role
        """
        return [msg for msg in self.history if msg.get("role") == role]
    
    def get_last_user_message(self) -> Optional[str]:
        """
        Get the content of the last user message.
        
        Returns:
            Content of the last user message, or None if no user messages exist
        """
        user_messages = self.get_user_messages()
        return user_messages[-1] if user_messages else None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """
        Get the content of the last assistant message.
        
        Returns:
            Content of the last assistant message, or None if no assistant messages exist
        """
        assistant_messages = self.get_assistant_messages()
        return assistant_messages[-1] if assistant_messages else None
