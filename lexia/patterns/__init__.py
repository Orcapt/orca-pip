"""
Design Patterns
===============

Implementation of common design patterns for Lexia SDK.
Professional-grade pattern implementations.

Patterns:
- Builder: Fluent interface for building complex objects
- Context Managers: Resource management
- Middleware: Request/response processing chain
"""

from .builder import LexiaBuilder, SessionBuilder
from .context import (
    SessionContext,
    ResourceContext,
    timed_operation,
    suppress_exceptions,
)
from .middleware import (
    Middleware,
    LoggingMiddleware,
    ValidationMiddleware,
    TransformMiddleware,
    MiddlewareChain,
    MiddlewareManager,
)

__all__ = [
    # Builder Pattern
    'LexiaBuilder',
    'SessionBuilder',
    # Context Managers
    'SessionContext',
    'ResourceContext',
    'timed_operation',
    'suppress_exceptions',
    # Middleware Pattern
    'Middleware',
    'LoggingMiddleware',
    'ValidationMiddleware',
    'TransformMiddleware',
    'MiddlewareChain',
    'MiddlewareManager',
]
