"""
Domain Module
=============

Domain models and interfaces.
Contains business entities and contracts.
"""

from .models import ChatResponse, ChatMessage, Variable, Memory, KnowledgeStore, ConnectedAgent
from .interfaces import (
    IStreamClient,
    IBufferManager,
    IButtonRenderer,
    ILoadingMarkerProvider,
    IUsageTracker,
    ITracingService,
    IErrorHandler,
    IAPIClient,
    IResponseBuilder
)

__all__ = [
    # Models
    'ChatResponse',
    'ChatMessage',
    'Variable',
    'Memory',
    'KnowledgeStore',
    'ConnectedAgent',
    # Interfaces
    'IStreamClient',
    'IBufferManager',
    'IButtonRenderer',
    'ILoadingMarkerProvider',
    'IUsageTracker',
    'ITracingService',
    'IErrorHandler',
    'IAPIClient',
    'IResponseBuilder',
]

