"""
Observability Module
====================

Production-grade observability and monitoring.

Components:
    - Metrics: Counter, Gauge, Histogram, Timer, MetricsCollector
    - Profiler: Performance profiling
    - Events: Event-driven architecture (pub/sub)
    - Monitor: System health monitoring
"""

from .metrics import (
    Counter,
    Gauge,
    Histogram,
    Timer,
    MetricsCollector,
    measure_time,
    get_metrics_collector,
)

from .profiler import (
    Profiler,
    profile,
    profile_async,
    profile_block,
)

from .events import (
    Event,
    EventListener,
    EventBus,
    get_event_bus,
)

from .monitor import (
    HealthStatus,
    HealthCheck,
    SystemMonitor,
)


__all__ = [
    # Metrics
    'Counter',
    'Gauge',
    'Histogram',
    'Timer',
    'MetricsCollector',
    'measure_time',
    'get_metrics_collector',
    
    # Profiler
    'Profiler',
    'profile',
    'profile_async',
    'profile_block',
    
    # Events
    'Event',
    'EventListener',
    'EventBus',
    'get_event_bus',
    
    # Monitor
    'HealthStatus',
    'HealthCheck',
    'SystemMonitor',
]
