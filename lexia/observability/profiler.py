"""
Profiler
========

Code profiling for performance optimization.
Identifies bottlenecks and performance issues.
"""

import time
import functools
import cProfile
import pstats
import io
from typing import Callable, Any, Optional, Dict, TypeVar
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class Profiler:
    """
    Code profiler for performance analysis.
    
    Example:
        >>> profiler = Profiler()
        >>> with profiler:
        ...     expensive_operation()
        >>> profiler.print_stats()
    """
    
    def __init__(self):
        """Initialize profiler."""
        self.profiler = cProfile.Profile()
        self._profiling = False
    
    def start(self) -> None:
        """Start profiling."""
        if not self._profiling:
            self.profiler.enable()
            self._profiling = True
            logger.debug("Profiling started")
    
    def stop(self) -> None:
        """Stop profiling."""
        if self._profiling:
            self.profiler.disable()
            self._profiling = False
            logger.debug("Profiling stopped")
    
    def __enter__(self) -> 'Profiler':
        """Enter context - start profiling."""
        self.start()
        return self
    
    def __exit__(self, *args) -> None:
        """Exit context - stop profiling."""
        self.stop()
    
    def print_stats(self, sort_by: str = 'cumulative', limit: int = 20) -> None:
        """
        Print profiling statistics.
        
        Args:
            sort_by: Sort key ('cumulative', 'time', 'calls', etc.)
            limit: Number of entries to show
        """
        stream = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats(sort_by)
        stats.print_stats(limit)
        
        logger.info(f"Profiling Results:\\n{stream.getvalue()}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get profiling statistics as dictionary.
        
        Returns:
            Dictionary with profiling stats
        """
        stream = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=stream)
        
        return {
            "total_calls": stats.total_calls,
            "primitive_calls": stats.prim_calls,
            "total_time": stats.total_tt,
        }


def profile(
    sort_by: str = 'cumulative',
    limit: int = 20,
    print_stats: bool = True
) -> Callable[[F], F]:
    """
    Decorator for profiling functions.
    
    Args:
        sort_by: Sort key for stats
        limit: Number of entries to show
        print_stats: Whether to print stats after execution
        
    Returns:
        Decorated function
        
    Example:
        >>> @profile(sort_by='time', limit=10)
        ... def expensive_function():
        ...     # Complex computation
        ...     pass
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = Profiler()
            
            with profiler:
                result = func(*args, **kwargs)
            
            if print_stats:
                logger.info(f"Profile results for {func.__name__}:")
                profiler.print_stats(sort_by, limit)
            
            return result
        
        return wrapper  # type: ignore
    return decorator


def profile_async(
    sort_by: str = 'cumulative',
    limit: int = 20
) -> Callable[[F], F]:
    """
    Decorator for profiling async functions.
    
    Args:
        sort_by: Sort key for stats
        limit: Number of entries to show
        
    Returns:
        Decorated async function
        
    Example:
        >>> @profile_async()
        ... async def async_operation():
        ...     await some_async_task()
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = Profiler()
            
            profiler.start()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                profiler.stop()
                logger.info(f"Profile results for {func.__name__}:")
                profiler.print_stats(sort_by, limit)
        
        return wrapper  # type: ignore
    return decorator


@contextmanager
def profile_block(name: str = "code_block"):
    """
    Context manager for profiling code blocks.
    
    Args:
        name: Name of the code block
        
    Example:
        >>> with profile_block("expensive_computation"):
        ...     result = complex_calculation()
    """
    profiler = Profiler()
    
    logger.info(f"Profiling {name}...")
    profiler.start()
    
    try:
        yield profiler
    finally:
        profiler.stop()
        profiler.print_stats()


__all__ = [
    'Profiler',
    'profile',
    'profile_async',
    'profile_block',
]

