# Design Patterns Guide

Complete guide to design patterns available in Orca SDK for professional code organization.

## Table of Contents

- [Overview](#overview)
- [Builder Pattern](#builder-pattern)
- [Middleware Pattern](#middleware-pattern)
- [Context Managers](#context-managers)
- [Best Practices](#best-practices)

## Overview

Orca SDK provides professional implementations of common design patterns:

- **Builder**: Fluent interface for complex object construction
- **Middleware**: Chain of responsibility for request processing
- **Context Managers**: Automatic resource management

## Builder Pattern

### OrcaBuilder

Build `OrcaHandler` with fluent interface:

```python
from orca.patterns import OrcaBuilder

# Simple builder
handler = (OrcaBuilder()
    .with_dev_mode(True)
    .build())

# With custom services
handler = (OrcaBuilder()
    .with_dev_mode(False)
    .with_buffer_manager(custom_buffer)
    .with_error_handler(custom_error_handler)
    .build())
```

### Full Configuration

```python
from orca.patterns import OrcaBuilder
from orca.services import BufferManager, ErrorHandler

handler = (OrcaBuilder()
    # Core settings
    .with_dev_mode(False)

    # Services
    .with_buffer_manager(BufferManager())
    .with_error_handler(ErrorHandler())
    .with_usage_tracker(custom_tracker)

    # Infrastructure
    .with_api_client(custom_api)
    .with_stream_client(custom_stream)

    # Build
    .build())
```

### SessionBuilder

Build session workflows with fluent interface:

```python
from orca.patterns import SessionBuilder

# Create builder with handler
builder = SessionBuilder(handler)

# Build and execute workflow
result = (builder
    .start_session(data)
    .show_loading("thinking")
    .process(lambda s: s.stream("Processing..."))
    .hide_loading("thinking")
    .add_button("Click", "https://example.com")
    .complete())  # Execute operations AND send to frontend
```

### Multi-step Workflow

```python
builder = SessionBuilder(handler)

# Complex workflow
result = (builder
    .start_session(data)

    # Step 1: Analysis
    .show_loading("analyzing")
    .track_trace("Analyzing input", "all")
    .process(analyze_input)
    .hide_loading("analyzing")

    # Step 2: Media content
    .add_video("https://example.com/video.mp4")
    .add_youtube("https://www.youtube.com/watch?v=...")
    .add_location_coordinates(35.6892, 51.3890)
    .add_card_list([
        {"photo": "https://example.com/card.jpg", "header": "Title", "text": "Content"}
    ])
    .add_audio_single("https://example.com/audio.mp3", label="Track")

    # Step 2: Processing
    .show_loading("processing")
    .track_trace("Processing data", "all")
    .process(process_data)
    .hide_loading("processing")

    # Step 3: Response
    .add_button("Regenerate", "regenerate")
    .add_button("Learn More", "https://docs.example.com")
    .track_usage(tokens=1500, token_type="gpt4", cost="0.03")

    # Complete - Execute operations AND send to frontend
    .complete())
```

### Custom Processing Steps

```python
def custom_step(session):
    """Custom processing step."""
    session.stream("Custom step")
    # ... custom logic ...

result = (builder
    .start_session(data)
    .process(custom_step)
    .complete())  # Execute and send to frontend
```

### Completing and Sending to Frontend

After building your workflow, you need to send the content to the frontend:

**Option 1: `complete()` - Recommended**

```python
# Executes all operations AND closes session (sends to frontend)
response = (builder
    .start_session(data)
    .show_loading("thinking")
    .add_stream("Processing...")
    .hide_loading("thinking")
    .complete())  # Returns full response string

print(response)  # Full response content
```

**Option 2: `close()` - Alias for complete()**

```python
response = (builder
    .start_session(data)
    .add_stream("Response")
    .close())  # Same as complete()
```

**Option 3: `finalize()` + Manual close**

```python
# finalize() only executes operations, doesn't close session
builder = (SessionBuilder(handler)
    .start_session(data)
    .add_stream("Processing...")
    .finalize())

# Manually close session to send to frontend
session = builder._session  # Access session directly
response = session.close()
```

**Option 4: `acomplete()` / `aclose()` - For Async Contexts**

```python
# Async version for use in async functions (FastAPI, async handlers, etc.)
async def handler(data):
    builder = SessionBuilder(handler).start_session(data)
    response = await builder.acomplete()  # Non-blocking!
    return response
```

**⚠️ Important:**

- Use `complete()` or `close()` for synchronous contexts
- Use `acomplete()` or `aclose()` for async contexts (FastAPI, async handlers, etc.)
- Use `finalize()` only if you need to execute operations without closing the session yet

## Middleware Pattern

### Middleware Basics

Chain of responsibility for request processing:

```python
from orca.patterns import Middleware, MiddlewareChain

class LoggingMiddleware(Middleware):
    def process(self, data, next_handler):
        print(f"Before: {data}")
        result = next_handler(data)
        print(f"After: {result}")
        return result

# Option 1: Using MiddlewareManager (recommended)
from orca.patterns import MiddlewareManager
manager = MiddlewareManager()
manager.use(LoggingMiddleware())

# Option 2: Using MiddlewareChain directly
from orca.patterns import MiddlewareChain
chain = MiddlewareChain()
chain.add(LoggingMiddleware())
```

### Built-in Middleware

#### LoggingMiddleware

```python
from orca.patterns import LoggingMiddleware

middleware = LoggingMiddleware(
    logger=my_logger,
    log_request=True,
    log_response=True,
    log_errors=True
)
```

#### ValidationMiddleware

```python
from orca.patterns import ValidationMiddleware

def validate_data(data):
    if not data.message:
        raise ValueError("Message is required")
    return True

middleware = ValidationMiddleware(validator=validate_data)
```

#### TransformMiddleware

```python
from orca.patterns import TransformMiddleware

def transform_request(data):
    # Modify request
    data.message = data.message.upper()
    return data

def transform_response(response):
    # Modify response
    return response.lower()

middleware = TransformMiddleware(
    request_transformer=transform_request,
    response_transformer=transform_response
)
```

### MiddlewareChain

Combine multiple middleware:

```python
from orca.patterns import MiddlewareChain

# Using MiddlewareManager (recommended - has execute method)
from orca.patterns import MiddlewareManager

manager = MiddlewareManager()

# Add middleware in order
manager.use(LoggingMiddleware())
manager.use(ValidationMiddleware(validator))
manager.use(TransformMiddleware(transform_request))
manager.use(AuthenticationMiddleware())

# Execute chain
def handler(data):
    return f"Processed: {data.message}"

result = manager.execute(handler, data)
```

### MiddlewareManager

Higher-level middleware management:

```python
from orca.patterns import MiddlewareManager

manager = MiddlewareManager()

# Register middleware
manager.register("logging", LoggingMiddleware())
manager.register("validation", ValidationMiddleware(validator))
manager.register("auth", AuthenticationMiddleware())

# Execute with specific middleware
result = manager.execute(
    data,
    handler,
    middleware=["logging", "validation", "auth"]
)

# Or execute all
result = manager.execute_all(data, handler)
```

### Custom Middleware

```python
from orca.patterns import Middleware, MiddlewareManager
import logging

class AuditMiddleware(Middleware):
    def process(self, data, next_handler):
        logging.info("Processing request %s from %s", data.message_uuid, data.channel)
        return next_handler(data)

# Use it
manager = MiddlewareManager()
manager.use(AuditMiddleware())
```

### Async Middleware

```python
from orca.patterns import Middleware

class AsyncCacheMiddleware(Middleware):
    async def process_async(self, data, next_handler):
        # Check cache
        cached = await self.get_cache(data.message)
        if cached:
            return cached

        # Process
        result = await next_handler(data)

        # Save to cache
        await self.set_cache(data.message, result)
        return result
```

## Context Managers

### SessionContext

Automatic session management:

```python
from orca.patterns import SessionContext

# Synchronous context (blocking operations)
with SessionContext(handler, data) as session:
    session.stream("Processing...")
    session.button.link("Click", "https://example.com")
    # Session automatically closes on exit
```

**⚠️ Important for Async Contexts:**

`SessionContext` uses blocking operations (`session.close()`) in `__exit__`.
For async contexts (FastAPI, async functions), manage the session manually:

```python
import asyncio
from orca import OrcaHandler

# Async-safe version
async def process_request(handler: OrcaHandler, data):
    session = handler.begin(data)
    try:
        session.stream("Processing...")
        session.button.link("Click", "https://example.com")
    finally:
        # Use asyncio.to_thread for non-blocking close
        await asyncio.to_thread(session.close)
```

### With Error Handling

```python
with SessionContext(handler, data) as session:
    try:
        session.stream("Processing...")
        risky_operation()
    except Exception as e:
        # Errors automatically handled
        pass
# Session closed, errors logged
```

### ResourceContext

Generic resource management:

```python
from orca.patterns import ResourceContext

class DatabaseConnection:
    def setup(self):
        print("Connecting...")

    def cleanup(self):
        print("Closing connection...")

with ResourceContext(DatabaseConnection()) as db:
    # Use database
    db.query("SELECT * FROM users")
# Automatically closes
```

### timed_operation

Measure execution time:

```python
from orca.patterns import timed_operation

# timed_operation logs the duration automatically
with timed_operation("database_query"):
    # Execute query
    results = db.query("SELECT * FROM users")
# Logs: "database_query took 0.234s"
```

### suppress_exceptions

Suppress specific exceptions:

```python
from orca.patterns import suppress_exceptions

with suppress_exceptions(ValueError, KeyError):
    # This won't crash the program
    value = risky_operation()
```

### Custom Context Managers

```python
from contextlib import contextmanager

@contextmanager
def transaction(db):
    """Database transaction context."""
    try:
        db.begin()
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

# Use it
with transaction(db) as tx:
    tx.execute("INSERT INTO users ...")
    tx.execute("UPDATE accounts ...")
```

## Best Practices

### 1. Use Builder for Complex Setup

```python
from orca.patterns import OrcaBuilder

# Good - clear configuration
handler = (OrcaBuilder()
    .with_dev_mode(False)
    .with_buffer_manager(custom_buffer)
    .with_error_handler(custom_error_handler)
    .build())

# Instead of
handler = OrcaHandler(
    dev_mode=False,
    buffer_manager=custom_buffer,
    error_handler=custom_error_handler
)
```

### 2. Use Middleware for Cross-cutting Concerns

```python
from orca.patterns import MiddlewareManager

manager = MiddlewareManager()
manager.use(LoggingMiddleware())      # Logging
manager.use(ValidationMiddleware())    # Validation
manager.use(AuthenticationMiddleware()) # Auth
# All concerns handled automatically
result = manager.execute(handler, data)
```

### 3. Use Context Managers for Cleanup

```python
from orca.patterns import SessionContext

# Automatic cleanup
with SessionContext(handler, data) as session:
    session.stream("Processing...")
    # No need to call session.close()
```

### 4. Combine Patterns

```python
from orca.patterns import (
    OrcaBuilder,
    MiddlewareChain,
    SessionContext,
    timed_operation
)

# Build handler
handler = OrcaBuilder().with_dev_mode(True).build()

# Setup middleware
from orca.patterns import MiddlewareManager
manager = MiddlewareManager()
manager.use(LoggingMiddleware())

# Use with context manager and timing
# timed_operation automatically logs the duration
with timed_operation("request_processing"):
    with SessionContext(handler, data) as session:
        result = manager.execute(lambda d: process_request(session, d), data)
# Logs: "request_processing took 1.234s"
```

## Integration Examples

### With Lambda

```python
from orca import LambdaAdapter
from orca.patterns import OrcaBuilder, MiddlewareManager

# Build handler
handler = (OrcaBuilder()
    .with_dev_mode(False)
    .build())

# Setup middleware
manager = MiddlewareManager()
manager.use(LoggingMiddleware())
manager.use(ValidationMiddleware())

adapter = LambdaAdapter()

@adapter.message_handler
async def process_message(data):
    def handler_func(d):
        session = handler.begin(d)
        session.stream("Response")
        session.close()

    # Execute through middleware
    manager.execute(handler_func, data)

def lambda_handler(event, context):
    return adapter.handle(event, context)
```

## See Also

- [Developer Guide](DEVELOPER_GUIDE.md) - Complete development guide
- [Examples](../../examples/patterns_example.py) - Working examples
