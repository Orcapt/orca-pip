"""
Observability Example
=====================

Demonstrates the complete observability system.
"""

import time
from lexia.observability import (
    get_metrics_collector,
    get_event_bus,
    SystemMonitor,
    profile,
    measure_time,
)


def main():
    """Main example."""
    print("🔥 Lexia Observability System Demo\n")
    
    # ============================================
    # 1. Metrics Collection
    # ============================================
    print("=" * 50)
    print("1. METRICS COLLECTION")
    print("=" * 50)
    
    collector = get_metrics_collector()
    
    # Counter - track events
    requests = collector.counter("http_requests_total")
    errors = collector.counter("http_errors_total")
    
    # Gauge - track current values
    active_connections = collector.gauge("active_connections")
    memory_usage = collector.gauge("memory_usage_bytes")
    
    # Histogram - track distributions
    response_time = collector.histogram("response_time_seconds")
    
    # Simulate some activity
    print("\n📊 Simulating activity...")
    for i in range(10):
        requests.inc()
        active_connections.set(i + 1)
        response_time.observe(0.1 * (i + 1))
        
        if i % 3 == 0:
            errors.inc()
    
    # Get metrics
    metrics = collector.get_metrics()
    print(f"\n✅ Total Requests: {metrics['http_requests_total']}")
    print(f"✅ Total Errors: {metrics['http_errors_total']}")
    print(f"✅ Active Connections: {metrics['active_connections']}")
    
    stats = response_time.stats
    print(f"✅ Response Time Stats:")
    print(f"   - Min: {stats['min']:.2f}s")
    print(f"   - Max: {stats['max']:.2f}s")
    print(f"   - Avg: {stats['avg']:.2f}s")
    print(f"   - Count: {stats['count']}")
    
    # ============================================
    # 2. Event System
    # ============================================
    print("\n" + "=" * 50)
    print("2. EVENT SYSTEM (Pub/Sub)")
    print("=" * 50)
    
    bus = get_event_bus()
    
    # Subscribe to events
    def on_user_login(event):
        user_id = event.data.get('user_id')
        print(f"✅ User {user_id} logged in!")
    
    def on_api_call(event):
        endpoint = event.data.get('endpoint')
        method = event.data.get('method')
        print(f"✅ API Call: {method} {endpoint}")
    
    def on_error(event):
        error = event.data.get('error')
        print(f"❌ Error occurred: {error}")
    
    # Register listeners
    bus.subscribe("user.login", on_user_login, priority=10)
    bus.subscribe("api.call", on_api_call, priority=5)
    bus.subscribe("error", on_error, priority=1)
    
    # Publish events
    print("\n📡 Publishing events...")
    bus.publish("user.login", {"user_id": 123, "ip": "127.0.0.1"})
    bus.publish("api.call", {"endpoint": "/api/users", "method": "GET"})
    bus.publish("error", {"error": "Connection timeout"})
    
    # Event history
    print("\n📜 Recent Events:")
    for event in bus.get_history(limit=3):
        print(f"   - {event.name}: {event.data}")
    
    # ============================================
    # 3. Performance Profiling
    # ============================================
    print("\n" + "=" * 50)
    print("3. PERFORMANCE PROFILING")
    print("=" * 50)
    
    # Profile with decorator
    @profile(sort_by='time', limit=5)
    def expensive_operation():
        """Simulate expensive operation."""
        result = 0
        for i in range(1000000):
            result += i ** 2
        return result
    
    print("\n⚡ Running profiled function...")
    result = expensive_operation()
    print(f"✅ Result: {result}")
    
    # Profile with context manager
    print("\n⚡ Profiling code block...")
    with measure_time("data_processing"):
        time.sleep(0.1)
        data = [i ** 2 for i in range(100000)]
    
    # ============================================
    # 4. System Monitoring
    # ============================================
    print("\n" + "=" * 50)
    print("4. SYSTEM MONITORING")
    print("=" * 50)
    
    monitor = SystemMonitor()
    
    # Get system stats
    stats = monitor.get_system_stats()
    print(f"\n💻 System Statistics:")
    print(f"   - CPU Usage: {stats['cpu_percent']:.1f}%")
    print(f"   - CPU Cores: {stats['cpu_count']}")
    print(f"   - Memory Total: {stats['memory_total'] / (1024**3):.2f} GB")
    print(f"   - Memory Used: {stats['memory_used'] / (1024**3):.2f} GB")
    print(f"   - Memory Available: {stats['memory_available'] / (1024**3):.2f} GB")
    print(f"   - Memory Usage: {stats['memory_percent']:.1f}%")
    print(f"   - Disk Total: {stats['disk_total'] / (1024**3):.2f} GB")
    print(f"   - Disk Used: {stats['disk_used'] / (1024**3):.2f} GB")
    print(f"   - Disk Free: {stats['disk_free'] / (1024**3):.2f} GB")
    print(f"   - Disk Usage: {stats['disk_percent']:.1f}%")
    
    # Add health checks
    def check_memory():
        """Check if memory usage is acceptable."""
        stats = monitor.get_system_stats()
        if stats['memory_percent'] < 90:
            return True, "Memory OK", {"usage": f"{stats['memory_percent']:.1f}%"}
        return False, "Memory high", {"usage": f"{stats['memory_percent']:.1f}%"}
    
    def check_disk():
        """Check if disk space is acceptable."""
        stats = monitor.get_system_stats()
        if stats['disk_percent'] < 90:
            return True, "Disk OK", {"usage": f"{stats['disk_percent']:.1f}%"}
        return False, "Disk full", {"usage": f"{stats['disk_percent']:.1f}%"}
    
    monitor.add_health_check("memory", check_memory, critical=True)
    monitor.add_health_check("disk", check_disk, critical=False)
    
    # Run health checks
    health = monitor.check_health()
    print(f"\n💊 Health Status:")
    print(f"   - Overall Healthy: {'✅' if health['healthy'] else '❌'}")
    print(f"   - Critical Failure: {'❌' if health['critical_failure'] else '✅'}")
    
    for name, result in health['checks'].items():
        status = "✅" if result['healthy'] else "❌"
        critical = "🔴" if result['critical'] else "🟡"
        print(f"   {status} {critical} {name}: {result['message']}")
    
    # ============================================
    # 5. Complete Example
    # ============================================
    print("\n" + "=" * 50)
    print("5. COMPLETE EXAMPLE")
    print("=" * 50)
    
    def process_request(user_id: int, endpoint: str):
        """Simulate request processing with full observability."""
        # Track request
        requests = collector.counter("api_requests")
        requests.inc()
        
        # Publish event
        bus.publish("request.started", {
            "user_id": user_id,
            "endpoint": endpoint
        })
        
        # Measure time
        with measure_time("request_processing"):
            try:
                # Simulate processing
                time.sleep(0.05)
                
                # Track response time
                response_time = collector.histogram("api_response_time")
                response_time.observe(0.05)
                
                # Success event
                bus.publish("request.completed", {
                    "user_id": user_id,
                    "endpoint": endpoint,
                    "status": 200
                })
                
                return {"status": "success"}
                
            except Exception as e:
                # Track error
                errors = collector.counter("api_errors")
                errors.inc()
                
                # Error event
                bus.publish("request.failed", {
                    "user_id": user_id,
                    "endpoint": endpoint,
                    "error": str(e)
                })
                
                raise
    
    # Subscribe to request events
    def on_request_started(event):
        print(f"   🚀 Request started: {event.data['endpoint']}")
    
    def on_request_completed(event):
        print(f"   ✅ Request completed: {event.data['endpoint']}")
    
    bus.subscribe("request.started", on_request_started)
    bus.subscribe("request.completed", on_request_completed)
    
    # Process some requests
    print("\n🔄 Processing requests...")
    for i in range(3):
        result = process_request(user_id=100 + i, endpoint=f"/api/data/{i}")
    
    print("\n" + "=" * 50)
    print("🔥 LEGENDARY Observability Demo Complete! 🔥")
    print("=" * 50)


if __name__ == "__main__":
    main()

