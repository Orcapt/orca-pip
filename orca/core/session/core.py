"""
Session Core
============

Core session class using composition.
Ultra-clean: Delegates to specialized operations classes.
"""

import logging
from typing import List, Optional
from urllib.parse import urlparse

from .loading_ops import LoadingOperations
from .image_ops import ImageOperations
from .video_ops import VideoOperations
from .location_ops import LocationOperations
from .card_ops import CardListOperations
from .audio_ops import AudioOperations
from .tracing_ops import TracingOperations
from .usage_ops import UsageOperations
from .button_ops import ButtonOperations
from .escalation_ops import EscalationOperations
from .html_ops import HtmlOperations
from ...helpers.button_helper import ButtonHelper

logger = logging.getLogger(__name__)


class Session:
    """
    Clean session using composition pattern.
    
    Responsibilities:
    - Coordinate operations via composition
    - Provide unified API
    - Delegate to specialized operations
    
    Design:
    - Composition over Inheritance
    - Single Responsibility (coordination only)
    - Each operation is a separate, focused class
    """
    
    def __init__(self, handler, data):
        """
        Initialize session with composition.
        
        Args:
            handler: Parent OrcaHandler
            data: Request data
        """
        self._handler = handler
        self._data = data
        
        # Core operations (public property access)
        self.loading = LoadingOperations(handler, data, self._stream_wrapper)
        self.image = ImageOperations(self._stream_wrapper, handler, data)
        self.video = VideoOperations(self._stream_wrapper)
        self.location = LocationOperations(self._stream_wrapper)
        self.card = CardListOperations(self._stream_wrapper)
        self.audio = AudioOperations(self._stream_wrapper)
        self.html = HtmlOperations(self._stream_wrapper)
        self.tracing = TracingOperations(handler, self._stream_wrapper)
        self.usage = UsageOperations(handler, data)
        self.escalation = EscalationOperations(handler, data)
        
        # Button helper (public namespace)
        self.button = ButtonHelper(self)
        
        # Deprecated button operations (for backwards compatibility)
        self._button_ops = ButtonOperations(self.button)
        self._button_ops.set_context(handler, self._stream_wrapper)
        
        # Preconfigure Centrifugo if provided
        if (not handler.dev_mode and 
            hasattr(data, 'stream_url') and 
            hasattr(data, 'stream_token')):
            handler.update_centrifugo_config(data.stream_url, data.stream_token)
    
    # ==================== Core Operations ====================
    
    def stream(self, content: str) -> None:
        """Stream content chunk."""
        self._handler.stream(self._data, content)
    
    def close(self, usage_info=None, file_url=None) -> str:
        """Complete response."""
        return self._handler.close(self._data, usage_info=usage_info, file_url=file_url)
    
    def error(self, error_message: str, exception: Exception = None, trace: str = None) -> None:
        """Send error."""
        self._handler.send_error(self._data, error_message, trace=trace, exception=exception)
    
    def escalate(
        self, 
        action: str = "human_handoff", 
        # summary: Optional[str] = None,  # Deactivated for now
        reason: Optional[str] = None
    ) -> bool:
        """
        Escalate conversation for human review.
        
        Args:
            action: Escalation action type (default: "human_handoff")
            # summary: Optional AI-generated summary  # Deactivated for now
            reason: Optional categorization/reason
            
        Returns:
            True if escalation succeeded, False otherwise
            
        Example:
            session.escalate(
                action="human_handoff",
                # summary="Customer needs refund assistance",  # Deactivated for now
                reason="refund_request"
            )
        """
        return self.escalation.escalate(action=action, reason=reason)
    
    # ==================== Agent-to-Agent Communication ====================
    
    @property
    def available_agents(self) -> list:
        """List of connected agents available for agent-to-agent calls."""
        return getattr(self._data, 'connected_agents', [])
    
    def ask_agent(self, slug: str, message: str, timeout: int = 120) -> str:
        """
        Ask a connected agent a question and wait for the response.
        
        Args:
            slug: The slug of the target agent
            message: The question/message to send
            timeout: Request timeout in seconds (default: 120)
            
        Returns:
            The agent's response content as a string
            
        Raises:
            ValueError: If slug is not in connected_agents list
            RuntimeError: If the request fails
        """
        available = [a.slug for a in self.available_agents]
        if slug not in available:
            raise ValueError(
                f"Agent '{slug}' is not connected. "
                f"Available agents: {available}"
            )
        
        parsed = urlparse(self._data.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        ask_url = f"{base_url}/api/internal/v1/agents/{slug}/ask"
        
        payload = {
            'message': message,
            'thread_id': self._data.thread_id,
            'conversation_id': self._data.conversation_id,
        }
        
        headers = getattr(self._data, 'headers', {}) or {}
        
        import requests
        try:
            logger.info(f"Asking agent '{slug}': {message[:100]}...")
            resp = requests.post(
                ask_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    **headers,
                },
                timeout=timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Agent '{slug}' raw response: {resp.text[:500]}")

            content = (
                data.get('content')
                or data.get('result', {}).get('content')
                or data.get('result', {}).get('message', {}).get('content')
                or data.get('data', {}).get('content')
                or ''
            )
            logger.info(f"Agent '{slug}' responded ({len(content)} chars)")
            return content
        except requests.exceptions.RequestException as e:
            logger.error(f"Agent-to-agent call to '{slug}' failed: {e}")
            raise RuntimeError(f"Failed to get response from agent '{slug}': {e}") from e
    
    # ==================== Wrapper for Delegation ====================
    
    def _stream_wrapper(self, content: str) -> None:
        """Internal wrapper for delegation."""
        self.stream(content)
    
    # ==================== Deprecated Methods (Backwards Compatibility) ====================
    
    def start_loading(self, kind: str = "thinking") -> None:
        """[DEPRECATED] Use session.loading.start_loading() instead."""
        self.loading.start(kind)
    
    def end_loading(self, kind: str = "thinking") -> None:
        """[DEPRECATED] Use session.loading.end_loading() instead."""
        self.loading.end(kind)
    
    def pass_image(self, url: str) -> None:
        """[DEPRECATED] Use session.image.image() instead."""
        self.image.send(url)
    
    def tracing(self, content: str, visibility: str = "all") -> None:
        """[DEPRECATED] Use session.tracing.begin() instead."""
        self.tracing.send(content, visibility)
    
    def tracing_begin(self, message: str, visibility: str = "all") -> None:
        """[DEPRECATED] Use session.tracing.begin() instead."""
        self.tracing.begin(message, visibility)
    
    def tracing_append(self, message: str) -> None:
        """[DEPRECATED] Use session.tracing.append() instead."""
        self.tracing.append(message)
    
    def tracing_end(self, message: str = None) -> None:
        """End progressive trace."""
        self._tracing.end(message)
    
    # ==================== Usage Operations ====================
    
    def usage(
        self,
        tokens: int,
        token_type: str,
        cost: Optional[str] = None,
        label: Optional[str] = None
    ) -> None:
        """Track usage."""
        self._usage.track(tokens, token_type, cost, label)
    
    # ==================== Deprecated Button Methods ====================
    
    def button_link(self, *args, **kwargs) -> None:
        """Deprecated: Use session.button.link()"""
        self._button_ops.button_link(*args, **kwargs)
    
    def button_action(self, *args, **kwargs) -> None:
        """Deprecated: Use session.button.action()"""
        self._button_ops.button_action(*args, **kwargs)
    
    def buttons_begin(self, *args, **kwargs) -> None:
        """Deprecated: Use session.button.begin()"""
        self._button_ops.buttons_begin(*args, **kwargs)
    
    def buttons_add_link(self, *args, **kwargs) -> None:
        """Deprecated: Use session.button.add_link()"""
        self._button_ops.buttons_add_link(*args, **kwargs)
    
    def buttons_add_action(self, *args, **kwargs) -> None:
        """Deprecated: Use session.button.add_action()"""
        self._button_ops.buttons_add_action(*args, **kwargs)
    
    def buttons_add_link_button(self, *args, **kwargs) -> None:
        """Deprecated"""
        self._button_ops.buttons_add_link_button(*args, **kwargs)
    
    def buttons_add_action_button(self, *args, **kwargs) -> None:
        """Deprecated"""
        self._button_ops.buttons_add_action_button(*args, **kwargs)
    
    def buttons_end(self, *args, **kwargs) -> None:
        """Deprecated: Use session.button.end()"""
        self._button_ops.buttons_end(*args, **kwargs)
    
    def buttons(self, *args, **kwargs) -> None:
        """Deprecated dictionary-based API"""
        self._button_ops.buttons(*args, **kwargs)

