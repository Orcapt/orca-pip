"""
Metrics Collection
==================

Professional-grade metrics collection system.
Tracks performance, usage, and system health.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class Counter:
    """
    Thread-safe counter for tracking events.
    
    Example:
        >>> counter = Counter("requests_total")
        >>> counter.inc()  # Increment by 1
        >>> counter.inc(5)  # Increment by 5
        >>> print(counter.value)  # Get current value
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize counter.
        
        Args:
            name: Metric name
            description: Metric description
        """
        self.name = name
        self.description = description
        self._value = 0
        self._lock = threading.Lock()
    
    def inc(self, amount: float = 1.0) -> None:
        """Increment counter."""
        with self._lock:
            self._value += amount
    
    def reset(self) -> None:
        """Reset counter to zero."""
        with self._lock:
            self._value = 0
    
    @property
    def value(self) -> float:
        """Get current value."""
        with self._lock:
            return self._value


class Gauge:
    """
    Thread-safe gauge for tracking current values.
    
    Example:
        >>> gauge = Gauge("memory_usage_bytes")
        >>> gauge.set(1024000)  # Set to specific value
        >>> gauge.inc(1000)     # Increase
        >>> gauge.dec(500)      # Decrease
    """
    
    def __init__(self, name: str, description: str = ""):
        """Initialize gauge."""
        self.name = name
        self.description = description
        self._value = 0.0
        self._lock = threading.Lock()
    
    def set(self, value: float) -> None:
        """Set gauge to specific value."""
        with self._lock:
            self._value = value
    
    def inc(self, amount: float = 1.0) -> None:
        """Increase gauge."""
        with self._lock:
            self._value += amount
    
    def dec(self, amount: float = 1.0) -> None:
        """Decrease gauge."""
        with self._lock:
            self._value -= amount
    
    @property
    def value(self) -> float:
        """Get current value."""
        with self._lock:
            return self._value


class Histogram:
    """
    Histogram for tracking distributions.
    
    Example:
        >>> hist = Histogram("request_duration_seconds")
        >>> hist.observe(0.5)  # Record 0.5 seconds
        >>> hist.observe(1.2)  # Record 1.2 seconds
        >>> stats = hist.stats  # Get statistics
    """
    
    def __init__(self, name: str, description: str = ""):
        """Initialize histogram."""
        self.name = name
        self.description = description
        self._observations: List[float] = []
        self._lock = threading.Lock()
    
    def observe(self, value: float) -> None:
        """Record an observation."""
        with self._lock:
            self._observations.append(value)
    
    @property
    def stats(self) -> Dict[str, float]:
        """Get statistics (min, max, avg, count)."""
        with self._lock:
            if not self._observations:
                return {"count": 0, "sum": 0, "min": 0, "max": 0, "avg": 0}
            
            return {
                "count": len(self._observations),
                "sum": sum(self._observations),
                "min": min(self._observations),
                "max": max(self._observations),
                "avg": sum(self._observations) / len(self._observations),
            }
    
    def reset(self) -> None:
        """Clear all observations."""
        with self._lock:
            self._observations.clear()


class Timer:
    """
    Timer for measuring durations.
    
    Example:
        >>> timer = Timer("operation_duration")
        >>> with timer:
        ...     perform_operation()
        >>> print(timer.duration)  # Get last duration
    """
    
    def __init__(self, name: str, description: str = ""):
        """Initialize timer."""
        self.name = name
        self.description = description
        self._start_time: Optional[float] = None
        self._duration: Optional[float] = None
        self.histogram = Histogram(f"{name}_seconds", description)
    
    def __enter__(self) -> 'Timer':
        """Start timer."""
        self._start_time = time.time()
        return self
    
    def __exit__(self, *args) -> None:
        """Stop timer and record duration."""
        if self._start_time is not None:
            self._duration = time.time() - self._start_time
            self.histogram.observe(self._duration)
            self._start_time = None
    
    @property
    def duration(self) -> Optional[float]:
        """Get last measured duration."""
        return self._duration


class MetricsCollector:
    """
    Central metrics collector.
    
    Manages all metrics in one place.
    
    Example:
        >>> collector = MetricsCollector()
        >>> requests = collector.counter("requests_total", "Total requests")
        >>> requests.inc()
        >>> 
        >>> # Get all metrics
        >>> metrics = collector.get_metrics()
    """
    
    def __init__(self):
        """Initialize collector."""
        self._metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def counter(self, name: str, description: str = "") -> Counter:
        """
        Get or create a counter.
        
        Args:
            name: Counter name
            description: Counter description
            
        Returns:
            Counter instance
        """
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Counter(name, description)
            return self._metrics[name]
    
    def gauge(self, name: str, description: str = "") -> Gauge:
        """Get or create a gauge."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Gauge(name, description)
            return self._metrics[name]
    
    def histogram(self, name: str, description: str = "") -> Histogram:
        """Get or create a histogram."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Histogram(name, description)
            return self._metrics[name]
    
    def timer(self, name: str, description: str = "") -> Timer:
        """Get or create a timer."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Timer(name, description)
            return self._metrics[name]
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as dictionary.
        
        Returns:
            Dictionary of all metrics with their current values
        """
        with self._lock:
            result = {}
            for name, metric in self._metrics.items():
                if isinstance(metric, (Counter, Gauge)):
                    result[name] = metric.value
                elif isinstance(metric, Histogram):
                    result[name] = metric.stats
                elif isinstance(metric, Timer):
                    result[name] = metric.histogram.stats
            return result
    
    def reset_all(self) -> None:
        """Reset all metrics."""
        with self._lock:
            for metric in self._metrics.values():
                if hasattr(metric, 'reset'):
                    metric.reset()


# Global metrics collector
_global_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return _global_collector


@contextmanager
def measure_time(metric_name: str, collector: Optional[MetricsCollector] = None):
    """
    Context manager to measure and record execution time.
    
    Args:
        metric_name: Name of the metric
        collector: Optional collector (uses global if None)
        
    Example:
        >>> with measure_time("api_request_duration"):
        ...     make_api_call()
    """
    if collector is None:
        collector = get_metrics_collector()
    
    timer = collector.timer(metric_name)
    
    with timer:
        yield timer


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return _global_collector


__all__ = [
    'Counter',
    'Gauge',
    'Histogram',
    'Timer',
    'MetricsCollector',
    'get_metrics_collector',
    'measure_time',
]

