"""
Event System
============

Event-driven architecture for extensibility.
Allows components to communicate via events.
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
import threading

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """
    Base event class.
    
    Example:
        >>> event = Event("user.created", {"user_id": 123})
        >>> print(event.name)
        'user.created'
    """
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation."""
        return f"Event({self.name}, data={self.data})"


class EventListener:
    """
    Event listener with priority and filtering.
    
    Example:
        >>> def handler(event):
        ...     print(f"Received: {event.name}")
        >>> 
        >>> listener = EventListener(handler, priority=10)
    """
    
    def __init__(
        self,
        callback: Callable[[Event], None],
        priority: int = 0,
        event_filter: Optional[Callable[[Event], bool]] = None
    ):
        """
        Initialize listener.
        
        Args:
            callback: Function to call when event occurs
            priority: Listener priority (higher = called first)
            event_filter: Optional filter function
        """
        self.callback = callback
        self.priority = priority
        self.event_filter = event_filter
    
    def should_handle(self, event: Event) -> bool:
        """Check if this listener should handle the event."""
        if self.event_filter is None:
            return True
        return self.event_filter(event)
    
    def handle(self, event: Event) -> None:
        """Handle the event."""
        try:
            self.callback(event)
        except Exception as e:
            logger.error(f"Error in event listener: {e}")


class EventBus:
    """
    Central event bus for publish/subscribe pattern.
    
    Thread-safe event dispatching with priorities.
    
    Example:
        >>> bus = EventBus()
        >>> 
        >>> def on_user_created(event):
        ...     print(f"User created: {event.data['user_id']}")
        >>> 
        >>> bus.subscribe("user.created", on_user_created)
        >>> bus.publish("user.created", {"user_id": 123})
    """
    
    def __init__(self):
        """Initialize event bus."""
        self._listeners: Dict[str, List[EventListener]] = {}
        self._lock = threading.Lock()
        self._event_history: List[Event] = []
        self._max_history = 100
    
    def subscribe(
        self,
        event_name: str,
        callback: Callable[[Event], None],
        priority: int = 0,
        event_filter: Optional[Callable[[Event], bool]] = None
    ) -> EventListener:
        """
        Subscribe to an event.
        
        Args:
            event_name: Name of event to subscribe to
            callback: Function to call when event occurs
            priority: Listener priority (higher = called first)
            event_filter: Optional filter function
            
        Returns:
            EventListener instance
            
        Example:
            >>> def handler(event):
            ...     print(event.data)
            >>> 
            >>> bus.subscribe("user.created", handler, priority=10)
        """
        listener = EventListener(callback, priority, event_filter)
        
        with self._lock:
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(listener)
            # Sort by priority (highest first)
            self._listeners[event_name].sort(key=lambda l: l.priority, reverse=True)
        
        logger.debug(f"Subscribed to event: {event_name} (priority={priority})")
        return listener
    
    def unsubscribe(self, event_name: str, listener: EventListener) -> None:
        """
        Unsubscribe a listener from an event.
        
        Args:
            event_name: Name of event
            listener: Listener to remove
        """
        with self._lock:
            if event_name in self._listeners:
                try:
                    self._listeners[event_name].remove(listener)
                    logger.debug(f"Unsubscribed from event: {event_name}")
                except ValueError:
                    pass
    
    def publish(
        self,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        Publish an event.
        
        Args:
            event_name: Name of event
            data: Event data
            metadata: Event metadata
            
        Returns:
            Created Event instance
            
        Example:
            >>> bus.publish("user.login", {"user_id": 123, "ip": "127.0.0.1"})
        """
        event = Event(
            name=event_name,
            data=data or {},
            metadata=metadata or {}
        )
        
        # Store in history
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        # Notify listeners
        listeners = self._get_listeners(event_name)
        for listener in listeners:
            if listener.should_handle(event):
                listener.handle(event)
        
        logger.debug(f"Published event: {event_name} (listeners={len(listeners)})")
        return event
    
    def _get_listeners(self, event_name: str) -> List[EventListener]:
        """Get listeners for an event."""
        with self._lock:
            return self._listeners.get(event_name, []).copy()
    
    def get_history(self, limit: int = 10) -> List[Event]:
        """
        Get recent event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        with self._lock:
            return self._event_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._event_history.clear()
    
    def has_listeners(self, event_name: str) -> bool:
        """Check if event has any listeners."""
        with self._lock:
            return event_name in self._listeners and len(self._listeners[event_name]) > 0


# Global event bus
_global_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get global event bus."""
    return _global_bus


__all__ = [
    'Event',
    'EventListener',
    'EventBus',
    'get_event_bus',
]

