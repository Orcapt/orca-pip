"""
Design Patterns Example
=======================

Demonstrates all design patterns available in Orca SDK.
"""

from orca import (
    OrcaBuilder,
    SessionBuilder,
    SessionContext,
    ResourceContext,
    timed_operation,
    suppress_exceptions,
    Middleware,
    LoggingMiddleware,
    ValidationMiddleware,
    TransformMiddleware,
    MiddlewareChain,
    MiddlewareManager,
)


def main():
    """Main example."""
    print("🎨 Orca Design Patterns Demo\n")
    
    # ============================================
    # 1. Builder Pattern
    # ============================================
    print("=" * 50)
    print("1. BUILDER PATTERN")
    print("=" * 50)
    print()
    
    # Build handler with fluent interface
    print("🏗️ Building handler with fluent interface...")
    handler = (
        OrcaBuilder()
        .with_dev_mode(True)
        .build()
    )
    print(f"✅ Handler created: {type(handler).__name__}")
    print()
    
    # ============================================
    # 2. Context Manager Pattern
    # ============================================
    print("=" * 50)
    print("2. CONTEXT MANAGER PATTERN")
    print("=" * 50)
    print()
    
    # Timed operation
    print("⏱️ Measuring operation time...")
    import time
    start = time.time()
    with timed_operation("data_processing"):
        # Simulate some work
        result = sum(i ** 2 for i in range(100000))
    duration = time.time() - start
    print(f"✅ Operation took: {duration:.4f}s")
    print()
    
    # Suppress exceptions
    print("🛡️ Suppressing non-critical exceptions...")
    with suppress_exceptions(ValueError, TypeError):
        # This would normally raise an error
        value = int("not a number")  # This will be suppressed
    print("✅ Exception suppressed, program continues")
    print()
    
    # ============================================
    # 3. Middleware Pattern
    # ============================================
    print("=" * 50)
    print("3. MIDDLEWARE PATTERN")
    print("=" * 50)
    print()
    
    # Create middleware chain
    print("🔗 Creating middleware chain...")
    chain = MiddlewareChain()
    
    # Add logging middleware
    chain.add(LoggingMiddleware())
    print("   ✅ Added: LoggingMiddleware")
    
    # Add validation middleware
    def validate_data(data):
        """Validate data has required fields."""
        if not isinstance(data, dict):
            return False
        if 'user_id' not in data:
            return False
        return True
    
    chain.add(ValidationMiddleware(validate_data))
    print("   ✅ Added: ValidationMiddleware")
    
    # Add transform middleware
    def transform_data(data):
        """Add timestamp to data."""
        import time
        data['timestamp'] = time.time()
        return data
    
    chain.add(TransformMiddleware(transform_data))
    print("   ✅ Added: TransformMiddleware")
    
    print()
    
    # Process data through middleware
    print("📤 Processing data through middleware chain...")
    test_data = {
        'user_id': 123,
        'action': 'login',
        'ip': '127.0.0.1'
    }
    
    processed_data = chain.process_request(test_data)
    print(f"✅ Data processed: {len(processed_data)} fields")
    print(f"   • Original fields: user_id, action, ip")
    print(f"   • Added by middleware: timestamp")
    print()
    
    # ============================================
    # 4. Middleware Chain Advanced
    # ============================================
    print("=" * 50)
    print("4. MIDDLEWARE CHAIN ADVANCED")
    print("=" * 50)
    print()
    
    print("🔄 Processing request and response...")
    advanced_chain = MiddlewareChain()
    advanced_chain.add(LoggingMiddleware())
    
    # Process request
    request_data = {'user_id': 456, 'action': 'test'}
    processed_request = advanced_chain.process_request(request_data)
    print(f"✅ Request processed: {len(processed_request)} fields")
    
    # Process response
    response_data = {"status": "success", "data": [1, 2, 3]}
    processed_response = advanced_chain.process_response(response_data, processed_request)
    print(f"✅ Response processed: {len(processed_response)} fields")
    print()
    
    # ============================================
    # 5. Custom Middleware
    # ============================================
    print("=" * 50)
    print("5. CUSTOM MIDDLEWARE")
    print("=" * 50)
    print()
    
    # Create custom middleware
    class AuthMiddleware(Middleware):
        """Custom authentication middleware."""
        
        def __init__(self, required_role="user"):
            self.required_role = required_role
        
        def process_request(self, data):
            """Check user authentication."""
            print(f"   🔐 Checking authentication (required: {self.required_role})...")
            
            # Add auth info
            data['authenticated'] = True
            data['role'] = self.required_role
            
            return data
        
        def process_response(self, response, request_data):
            """Add auth headers to response."""
            response['auth_checked'] = True
            return response
    
    # Use custom middleware
    print("🔧 Creating custom authentication middleware...")
    custom_chain = MiddlewareChain()
    custom_chain.add(AuthMiddleware(required_role="admin"))
    
    processed = custom_chain.process_request({'user_id': 456})
    print(f"✅ Custom middleware applied")
    print(f"   • authenticated: {processed.get('authenticated')}")
    print(f"   • role: {processed.get('role')}")
    print()
    
    # ============================================
    # 6. Complete Example
    # ============================================
    print("=" * 50)
    print("6. COMPLETE EXAMPLE")
    print("=" * 50)
    print()
    
    print("🚀 Building complete request pipeline...")
    
    # Build handler
    handler = (
        OrcaBuilder()
        .with_dev_mode(True)
        .build()
    )
    
    # Setup middleware
    pipeline = MiddlewareChain()
    pipeline.add(AuthMiddleware(required_role="user"))
    pipeline.add(LoggingMiddleware())
    
    def process_request_data(data):
        """Validate request data."""
        return 'user_id' in data and 'action' in data
    
    pipeline.add(ValidationMiddleware(process_request_data))
    
    # Process request
    request = {
        'user_id': 789,
        'action': 'get_data',
        'filters': {'status': 'active'}
    }
    
    print("📥 Processing request...")
    with timed_operation("request_pipeline"):
        processed = pipeline.process_request(request)
    
    print(f"✅ Request processed successfully!")
    print(f"   • Fields: {len(processed)}")
    print(f"   • Authenticated: {processed.get('authenticated')}")
    print(f"   • Role: {processed.get('role')}")
    print()
    
    # ============================================
    # Summary
    # ============================================
    print("=" * 50)
    print("📊 PATTERNS SUMMARY")
    print("=" * 50)
    print()
    print("Available Patterns:")
    print("  1️⃣ Builder Pattern")
    print("     • OrcaBuilder - Fluent handler construction")
    print("     • SessionBuilder - Multi-step session flows")
    print()
    print("  2️⃣ Context Managers")
    print("     • SessionContext - Automatic cleanup")
    print("     • ResourceContext - Resource management")
    print("     • timed_operation - Performance monitoring")
    print("     • suppress_exceptions - Error handling")
    print()
    print("  3️⃣ Middleware Pattern")
    print("     • Middleware - Base class")
    print("     • LoggingMiddleware - Request/response logging")
    print("     • ValidationMiddleware - Data validation")
    print("     • TransformMiddleware - Data transformation")
    print("     • MiddlewareChain - Chain of responsibility")
    print("     • MiddlewareManager - Pipeline execution")
    print()
    
    print("=" * 50)
    print("🔥 DESIGN PATTERNS DEMO COMPLETE! 🔥")
    print("=" * 50)


if __name__ == "__main__":
    main()

