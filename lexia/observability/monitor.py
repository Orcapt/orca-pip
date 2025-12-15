"""
System Monitor
==============

System health monitoring and checks.
"""

import time
import psutil
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health check status."""
    healthy: bool
    message: str
    details: Dict[str, Any]
    timestamp: float


class HealthCheck:
    """
    Single health check.
    
    Example:
        >>> def check_db():
        ...     # Check database connection
        ...     return True, "Database OK", {}
        >>> 
        >>> health = HealthCheck("database", check_db)
        >>> status = health.check()
    """
    
    def __init__(
        self,
        name: str,
        check_func: Callable[[], tuple[bool, str, Dict[str, Any]]],
        critical: bool = True
    ):
        """
        Initialize health check.
        
        Args:
            name: Name of the check
            check_func: Function that returns (healthy, message, details)
            critical: Whether this check is critical
        """
        self.name = name
        self.check_func = check_func
        self.critical = critical
    
    def check(self) -> HealthStatus:
        """
        Run the health check.
        
        Returns:
            HealthStatus
        """
        try:
            healthy, message, details = self.check_func()
            return HealthStatus(
                healthy=healthy,
                message=message,
                details=details,
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"Health check '{self.name}' failed: {e}")
            return HealthStatus(
                healthy=False,
                message=f"Check failed: {e}",
                details={"error": str(e)},
                timestamp=time.time()
            )


class SystemMonitor:
    """
    System monitoring for resource usage.
    
    Example:
        >>> monitor = SystemMonitor()
        >>> stats = monitor.get_system_stats()
        >>> print(f"CPU: {stats['cpu_percent']}%")
        >>> print(f"Memory: {stats['memory_percent']}%")
    """
    
    def __init__(self):
        """Initialize system monitor."""
        self._health_checks: List[HealthCheck] = []
    
    def add_health_check(
        self,
        name: str,
        check_func: Callable[[], tuple[bool, str, Dict[str, Any]]],
        critical: bool = True
    ) -> None:
        """
        Add a health check.
        
        Args:
            name: Name of the check
            check_func: Check function
            critical: Whether this check is critical
        """
        check = HealthCheck(name, check_func, critical)
        self._health_checks.append(check)
        logger.info(f"Added health check: {name} (critical={critical})")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get current system statistics.
        
        Returns:
            Dictionary with CPU, memory, disk usage, etc.
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_count": psutil.cpu_count(),
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_used": memory.used,
                "memory_percent": memory.percent,
                "disk_total": disk.total,
                "disk_used": disk.used,
                "disk_free": disk.free,
                "disk_percent": disk.percent,
                "timestamp": time.time(),
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    def check_health(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Dictionary with overall health status and individual check results
        """
        results = {}
        all_healthy = True
        critical_failure = False
        
        for check in self._health_checks:
            status = check.check()
            results[check.name] = {
                "healthy": status.healthy,
                "message": status.message,
                "details": status.details,
                "critical": check.critical,
                "timestamp": status.timestamp,
            }
            
            if not status.healthy:
                all_healthy = False
                if check.critical:
                    critical_failure = True
        
        return {
            "healthy": all_healthy,
            "critical_failure": critical_failure,
            "checks": results,
            "timestamp": time.time(),
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information."""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "virtual": {
                    "total": mem.total,
                    "available": mem.available,
                    "used": mem.used,
                    "free": mem.free,
                    "percent": mem.percent,
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                }
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {"error": str(e)}
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information."""
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_times = psutil.cpu_times()
            
            return {
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True),
                "percent": psutil.cpu_percent(interval=0.1),
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None,
                },
                "times": {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "idle": cpu_times.idle,
                }
            }
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            return {"error": str(e)}


__all__ = [
    'HealthStatus',
    'HealthCheck',
    'SystemMonitor',
]

