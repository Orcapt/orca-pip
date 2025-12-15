"""
Builder Pattern
===============

Fluent interface for building complex objects.
Provides a clean, readable API for object construction.
"""

from typing import Optional, Dict, Any, List
from ..config import LoadingKind, ButtonColor
import logging

logger = logging.getLogger(__name__)


class LexiaBuilder:
    """
    Builder for LexiaHandler with fluent interface.
    
    Provides a clean, readable way to construct LexiaHandler with custom configuration.
    
    Example:
        >>> handler = (LexiaBuilder()
        ...     .with_dev_mode(True)
        ...     .with_buffer_size(2000)
        ...     .with_timeout(60)
        ...     .build())
    """
    
    def __init__(self):
        """Initialize builder with default values."""
        self._dev_mode: Optional[bool] = None
        self._stream_client = None
        self._api_client = None
        self._buffer_manager = None
        self._button_renderer = None
        self._loading_marker_provider = None
        self._usage_tracker = None
        self._tracing_service = None
        self._error_handler = None
        self._response_builder = None
        self._custom_config: Dict[str, Any] = {}
    
    def with_dev_mode(self, enabled: bool = True) -> 'LexiaBuilder':
        """
        Enable or disable development mode.
        
        Args:
            enabled: Whether to enable dev mode
            
        Returns:
            Self for chaining
        """
        self._dev_mode = enabled
        return self
    
    def with_stream_client(self, client: Any) -> 'LexiaBuilder':
        """
        Set custom stream client.
        
        Args:
            client: Custom stream client
            
        Returns:
            Self for chaining
        """
        self._stream_client = client
        return self
    
    def with_api_client(self, client: Any) -> 'LexiaBuilder':
        """Set custom API client."""
        self._api_client = client
        return self
    
    def with_buffer_manager(self, manager: Any) -> 'LexiaBuilder':
        """Set custom buffer manager."""
        self._buffer_manager = manager
        return self
    
    def with_config(self, key: str, value: Any) -> 'LexiaBuilder':
        """
        Set custom configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            Self for chaining
        """
        self._custom_config[key] = value
        return self
    
    def build(self) -> Any:
        """
        Build and return LexiaHandler instance.
        
        Returns:
            Configured LexiaHandler instance
        """
        from ..core import LexiaHandler
        
        return LexiaHandler(
            dev_mode=self._dev_mode,
            stream_client=self._stream_client,
            api_client=self._api_client,
            buffer_manager=self._buffer_manager,
            button_renderer=self._button_renderer,
            loading_marker_provider=self._loading_marker_provider,
            usage_tracker=self._usage_tracker,
            tracing_service=self._tracing_service,
            error_handler=self._error_handler,
            response_builder=self._response_builder,
        )


class SessionBuilder:
    """
    Builder for constructing complex session interactions.
    
    Provides a fluent interface for building multi-step session flows.
    
    Example:
        >>> session_flow = (SessionBuilder(session)
        ...     .add_loading(LoadingKind.THINKING)
        ...     .add_stream("Processing...")
        ...     .add_button_link("Click", "https://example.com")
        ...     .build())
    """
    
    def __init__(self, session: Any):
        """
        Initialize builder with session.
        
        Args:
            session: Session instance to build on
        """
        self._session = session
        self._operations: List[Dict[str, Any]] = []
    
    def add_loading(
        self,
        kind: str = LoadingKind.THINKING.value,
        action: str = "start"
    ) -> 'SessionBuilder':
        """
        Add loading indicator operation.
        
        Args:
            kind: Type of loading
            action: 'start' or 'end'
            
        Returns:
            Self for chaining
        """
        self._operations.append({
            "type": "loading",
            "kind": kind,
            "action": action,
        })
        return self
    
    def add_stream(self, content: str) -> 'SessionBuilder':
        """
        Add stream operation.
        
        Args:
            content: Content to stream
            
        Returns:
            Self for chaining
        """
        self._operations.append({
            "type": "stream",
            "content": content,
        })
        return self
    
    def add_button_link(
        self,
        label: str,
        url: str,
        row: int = 1,
        color: Optional[str] = None
    ) -> 'SessionBuilder':
        """
        Add link button operation.
        
        Args:
            label: Button label
            url: Button URL
            row: Button row
            color: Button color
            
        Returns:
            Self for chaining
        """
        self._operations.append({
            "type": "button_link",
            "label": label,
            "url": url,
            "row": row,
            "color": color or ButtonColor.PRIMARY.value,
        })
        return self
    
    def add_button_action(
        self,
        label: str,
        action_id: str,
        row: int = 1,
        color: Optional[str] = None
    ) -> 'SessionBuilder':
        """Add action button operation."""
        self._operations.append({
            "type": "button_action",
            "label": label,
            "action_id": action_id,
            "row": row,
            "color": color or ButtonColor.PRIMARY.value,
        })
        return self
    
    def add_image(self, url: str) -> 'SessionBuilder':
        """Add image operation."""
        self._operations.append({
            "type": "image",
            "url": url,
        })
        return self
    
    def add_tracing(
        self,
        message: str,
        visibility: str = "all"
    ) -> 'SessionBuilder':
        """Add tracing operation."""
        self._operations.append({
            "type": "tracing",
            "message": message,
            "visibility": visibility,
        })
        return self
    
    def execute(self) -> None:
        """
        Execute all queued operations on the session.
        
        This method runs all operations that were added via the builder.
        """
        for op in self._operations:
            op_type = op["type"]
            
            if op_type == "loading":
                if op["action"] == "start":
                    self._session.start_loading(op["kind"])
                else:
                    self._session.end_loading(op["kind"])
            
            elif op_type == "stream":
                self._session.stream(op["content"])
            
            elif op_type == "button_link":
                self._session.button.link(
                    op["label"],
                    op["url"],
                    row=op["row"],
                    color=op["color"]
                )
            
            elif op_type == "button_action":
                self._session.button.action(
                    op["label"],
                    op["action_id"],
                    row=op["row"],
                    color=op["color"]
                )
            
            elif op_type == "image":
                self._session.image(op["url"])
            
            elif op_type == "tracing":
                self._session.tracing(op["message"], op["visibility"])
        
        logger.info(f"Executed {len(self._operations)} operations")
    
    def build(self) -> 'SessionBuilder':
        """
        Build (execute) the session flow.
        
        Returns:
            Self for final operations
        """
        self.execute()
        return self


__all__ = [
    'LexiaBuilder',
    'SessionBuilder',
]

