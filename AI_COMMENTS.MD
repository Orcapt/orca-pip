# AI Developer Review: Orca SDK

*Review Date: December 30, 2025*

---

## 🎯 Overall Verdict: **Yes, I Would Use This Library**

As a developer, I would consider using this SDK for building real-time AI agent applications. Here's my honest breakdown:

---

## ✅ What's Developer-Friendly

### 1. **Clean, Intuitive Core API**

The main API is beautifully simple:

```python
handler = OrcaHandler(dev_mode=True)
session = handler.begin(data)
session.stream("Hello, world!")
session.close()
```

This is exactly what developers want - minimal boilerplate, clear flow. The `session.stream()` / `session.close()` pattern is intuitive and follows natural conversation flow.

### 2. **Excellent Namespace Organization (session.X.action)**

The use of namespaced operations is fantastic:

```python
session.loading.start("thinking")
session.button.link("Click me", "https://...")
session.tracing.begin("Step 1")
session.image.send("https://...")
session.video.youtube("https://...")
session.usage.track(tokens=100, token_type="gpt4")
```

This is much better than having 50+ flat methods on the session. It's discoverable, organized, and IDE autocomplete-friendly.

### 3. **Solid Dev Mode**

Having `dev_mode=True` that works without Centrifugo or external dependencies is excellent for local development. Many SDKs fail here - they require the full production setup even to test locally.

### 4. **Factory Pattern for Quick Setup**

```python
app = create_agent_app(process_message_func=process_msg)
```

One line to get a production-ready FastAPI app? This is exactly what developers need for rapid prototyping.

### 5. **Comprehensive Exception Hierarchy**

The exception design is professional:

```python
OrcaException (base)
├── ConfigurationError
├── ValidationError  
├── CommunicationError
│   ├── StreamError
│   └── APIError
└── BufferError
```

Each exception has `message`, `details`, and `to_dict()` - very useful for logging and debugging.

### 6. **Useful Decorators**

```python
@retry(max_attempts=3, delay=1.0)
@measure_time
@log_execution(include_args=True)
```

These are practical utilities that reduce boilerplate. The `@deprecated` decorator is also a nice touch for API evolution.

### 7. **Rich Media Support**

The support for images, videos, YouTube, audio, location, and card lists shows thoughtful design for real AI assistant use cases.

---

## ⚠️ Areas of Concern / Suggestions

### 1. **`__init__.py` Exports Too Much**

The main `__init__.py` exports ~70+ symbols. While comprehensive, this can be overwhelming:

```python
from orca import (
    OrcaHandler, Session, ChatMessage, Variable, Memory,
    LambdaAdapter, create_lambda_handler, BufferManager,
    ButtonRenderer, TracingService, ErrorHandler, ResponseBuilder,
    OrcaBuilder, SessionBuilder, SessionContext, ResourceContext,
    timed_operation, suppress_exceptions, Middleware, LoggingMiddleware,
    ValidationMiddleware, TransformMiddleware, MiddlewareChain, ...
)
```

**Suggestion:** Consider tiered exports:
- Core: `from orca import OrcaHandler, ChatMessage, create_agent_app` (10-15 items)
- Advanced: `from orca.patterns import SessionBuilder, Middleware`
- Internals: `from orca.services import BufferManager`

### 2. **Deprecation Clutter in Session**

The `Session` class has many deprecated methods:

```python
def start_loading(self, kind: str = "thinking") -> None:
    """[DEPRECATED] Use session.loading.start_loading() instead."""

def pass_image(self, url: str) -> None:
    """[DEPRECATED] Use session.image.image() instead."""
```

This works, but it adds cognitive overhead. Consider moving deprecated methods to a separate mixin or removing them in the next major version.

### 3. **Inconsistent Method Naming in Some Places**

```python
session.image.send(url)      # ✅ send
session.video.send(url)      # ✅ send
session.audio.send(tracks)   # ✅ send
session.location.send(coords) # ✅ send
session.button.link(...)      # 🤔 not "send"
```

`button.link()` immediately sends, but isn't named `send`. This is minor but can be confusing.

### 4. **SessionBuilder Has Two Streaming Modes**

```python
builder.add_stream("Hello")  # Queued
builder.stream("Hello")      # Immediate
```

Having both `add_stream()` (queued) and `stream()` (immediate) on the same builder might confuse developers. Consider making the builder purely queue-based.

### 5. **Documentation Discrepancy**

In `main.py` example:

```python
session = orca.begin(data)  # Uses 'orca' handler
```

But `orca` is the returned handler, not imported. This works but may confuse readers who skim the code.

### 6. **ChatMessage Has Many Fields**

```python
class ChatMessage(BaseModel):
    thread_id: str
    model: str
    message: str
    conversation_id: int
    response_uuid: str
    message_uuid: str
    channel: str
    file_type: str = ""
    file_url: str = ""
    file_base64: str = ""
    file_name: str = ""
    variables: List[Variable]
    url: str
    url_update: str = ""
    url_upload: str = ""
    force_tools: Optional[List[str]] = None
    system_message: Optional[str] = None
    memory: Union[Memory, Dict[str, Any], List] = Memory()
    # ... more
```

This is clearly dictated by the Orca platform, but it's a lot for developers to understand. A diagram or table in docs explaining what each field does would help.

---

## 📊 Architecture Assessment

### Strengths:
- ✅ **SOLID principles** applied correctly
- ✅ **Dependency injection** in `OrcaHandler`
- ✅ **Composition over inheritance** in Session
- ✅ **Facade pattern** in Storage client
- ✅ **Builder pattern** for complex configurations
- ✅ **Interfaces defined** in `domain/interfaces.py`

### The Layer Structure is Professional:
```
orca/
├── core/           # Business logic
├── domain/         # Models & interfaces
├── services/       # Single-responsibility services
├── infrastructure/ # External communication
├── patterns/       # Builder, middleware, etc.
├── adapters/       # Lambda, etc.
└── storage/        # Storage SDK
```

This is enterprise-grade architecture. Good for a production SDK.

---

## 🎨 Code Quality Observations

### Good:
- Consistent docstrings with examples
- Type hints throughout
- Proper logging with `__name__`
- Enums for constants (`LoadingKind`, `ButtonColor`)
- Configuration centralized in `config.py`

### Could Improve:
- Some files are very long (`builder.py` is 745 lines)
- `Session.tracing` property shadows the `tracing` method (line 109 vs line 59)
- Test coverage appears limited (only `test_package.py` and `test_refactored.py` visible)

---

## 📚 Documentation Quality

**Excellent.** The `docs/guides/` folder has:
- `QUICK_REFERENCE.md` - Cheat sheet style (great!)
- `DEVELOPER_GUIDE.md` - Full walkthrough
- `API_REFERENCE.md` - Complete API docs
- `PATTERNS_GUIDE.md` - Design patterns
- `LAMBDA_DEPLOY_GUIDE.md` - AWS deployment
- `DEV_MODE_GUIDE.md` - Local development

The README has a good quick start and the examples folder is comprehensive.

---

## 🚀 My Ideal Usage Flow

If I were building an AI agent, here's how I'd use this SDK:

```python
from orca import create_agent_app, ChatMessage, OrcaHandler

async def my_agent(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)
    
    try:
        session.loading.start("thinking")
        
        # My AI logic here
        response = await call_openai(data.message)
        
        session.loading.end("thinking")
        session.stream(response)
        
        session.button.action("Regenerate", "regenerate")
        session.close()
        
    except Exception as e:
        session.error("Something went wrong", exception=e)

app = create_agent_app(process_message_func=my_agent)
```

This is clean, readable, and production-ready. That's exactly what I want from an SDK.

---

## 📈 Final Scores

| Category | Score | Notes |
|----------|-------|-------|
| **API Design** | 9/10 | Clean, intuitive, namespaced |
| **Documentation** | 9/10 | Comprehensive guides and examples |
| **Architecture** | 8/10 | SOLID, clean layers, good DI |
| **Developer Experience** | 8/10 | Great dev mode, easy setup |
| **Code Quality** | 8/10 | Good typing, could use more tests |
| **Maintainability** | 7/10 | Deprecations add clutter |

**Overall: 8.2/10** - A solid, professional SDK that I would recommend for building AI agents on the Orca platform.

---

## 💡 Recommendations for the Team

1. **Add more unit tests** - I only see 2 test files. Aim for >80% coverage.
2. **Consider a "slim" import mode** - For developers who only need the basics.
3. **Remove deprecated methods** in v2.0 to clean up the codebase.
4. **Add type stubs** (`.pyi` files) for even better IDE support.
5. **Consider async-first design** - Many AI operations are async; make the SDK native async with sync wrappers.
6. **Add integration test examples** - Show how to test agents using the SDK.

---

## 🏗️ Proposal: Unified Handler Architecture

### The Problem

Currently, developers need to think about deployment when writing their agent:

```python
# For FastAPI / HTTP
app = create_agent_app(process_message_func=my_agent)

# For Lambda
handler = create_hybrid_handler(process_message_func=my_agent)

# For SQS
# Different setup...
```

This creates cognitive overhead. Developers should focus on **agent logic**, not **infrastructure**.

---

### The Vision: Write Once, Deploy Anywhere (Zero Code Changes)

**The developer writes ONE file. That's it.**

```python
# agent.py - This is the ONLY code the developer writes
from orca import Agent

@Agent.handler
async def my_agent(session):
    """
    Pure agent logic. No deployment concerns.
    Works the same whether deployed to Lambda, FastAPI, SQS, or local dev.
    """
    session.loading.start("thinking")
    
    response = await call_ai(session.message)
    
    session.loading.end("thinking")
    session.stream(response)
    session.button.action("Regenerate", "regenerate")
    
    # No need to call session.close() - handled automatically
```

**The SDK auto-detects the runtime environment. No code changes needed.**

```bash
# Local development
python agent.py
# SDK detects: no Lambda context → runs as local HTTP server

# Lambda deployment  
# SDK detects: AWS_LAMBDA_FUNCTION_NAME exists → runs as Lambda handler

# Docker/Kubernetes
docker run my-agent
# SDK detects: ORCA_RUNTIME=http → runs as HTTP server

# SQS Worker
ORCA_RUNTIME=sqs python agent.py
# SDK detects: SQS mode → polls queue
```

---

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer's Agent Code                   │
│                        (agent.py)                            │
│                                                              │
│   @Agent.handler                                             │
│   async def my_agent(session):                               │
│       session.stream("Hello!")   ←── SAME CODE EVERYWHERE    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   SmartStreamClient                          │
│            (auto-selects backend based on env)               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Dev Backend  │    │ HTTP Backend  │    │Lambda Backend │
│               │    │               │    │               │
│  In-memory    │    │  Centrifugo   │    │  SQS Queue    │
│  Console log  │    │  (direct)     │    │      │        │
│               │    │      │        │    │      ▼        │
│      ▼        │    │      ▼        │    │   Worker      │
│  [Developer   │    │  [User sees   │    │      │        │
│   sees logs]  │    │   streaming]  │    │      ▼        │
│               │    │               │    │  Centrifugo   │
│               │    │               │    │      │        │
│               │    │               │    │      ▼        │
│               │    │               │    │  [User sees   │
│               │    │               │    │   streaming]  │
└───────────────┘    └───────────────┘    └───────────────┘

     Detected:            Detected:            Detected:
   No CENTRIFUGO_URL    CENTRIFUGO_URL     AWS_LAMBDA_FUNCTION_NAME
```

**The developer writes `session.stream()` once. The SDK routes it correctly based on environment.**

---

### Implementation Idea

#### 1. Runtime & Mode Auto-Detection

```python
import os

class RuntimeDetector:
    """Automatically detect runtime AND mode (dev/production)."""
    
    @staticmethod
    def detect_runtime() -> str:
        """Detect WHERE the code is running."""
        # 1. Explicit override
        if os.environ.get("ORCA_RUNTIME"):
            return os.environ["ORCA_RUNTIME"]
        
        # 2. Auto-detect Lambda
        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            return "lambda"
        
        # 3. Auto-detect SQS
        if os.environ.get("ORCA_SQS_QUEUE_URL"):
            return "sqs"
        
        # 4. Default to HTTP
        return "http"
    
    @staticmethod
    def detect_mode() -> str:
        """Detect HOW to stream (dev vs production)."""
        # 1. Explicit override
        if os.environ.get("ORCA_DEV_MODE", "").lower() in ("true", "1", "yes"):
            return "dev"
        
        # 2. Production if Centrifugo is configured
        if os.environ.get("CENTRIFUGO_URL") or os.environ.get("STREAM_URL"):
            return "production"
        
        # 3. Default to dev (safe for local development)
        return "dev"
    
    @staticmethod
    def detect() -> dict:
        """Full detection."""
        return {
            "runtime": RuntimeDetector.detect_runtime(),  # http, lambda, sqs
            "mode": RuntimeDetector.detect_mode(),        # dev, production
        }
```

#### 2. Smart Stream Client (Auto-Routes Based on Runtime)

```python
class SmartStreamClient:
    """
    The magic: same interface, different backends.
    Developer calls session.stream() - SDK figures out the rest.
    """
    
    def __init__(self):
        self.runtime = RuntimeDetector.detect_runtime()
        self.mode = RuntimeDetector.detect_mode()
        
        # Choose backend based on runtime
        if self.runtime == "lambda":
            # Lambda can't stream directly - use SQS
            self._backend = SQSStreamBackend()
        elif self.mode == "dev":
            # Dev mode - in-memory, console output
            self._backend = DevStreamBackend()
        else:
            # HTTP/Docker production - direct Centrifugo
            self._backend = CentrifugoStreamBackend()
    
    def send_delta(self, channel, response_uuid, thread_id, content):
        """Same interface regardless of backend."""
        self._backend.send_delta(channel, response_uuid, thread_id, content)


class SQSStreamBackend:
    """For Lambda: Queue messages to SQS instead of streaming directly."""
    
    def send_delta(self, channel, response_uuid, thread_id, content):
        # Queue to SQS - a worker will pick this up and stream via Centrifugo
        sqs.send_message(
            QueueUrl=os.environ["ORCA_STREAM_QUEUE_URL"],
            MessageBody=json.dumps({
                "action": "stream",
                "channel": channel,
                "response_uuid": response_uuid,
                "thread_id": thread_id,
                "content": content
            })
        )


class CentrifugoStreamBackend:
    """For HTTP/Docker: Stream directly to Centrifugo."""
    
    def send_delta(self, channel, response_uuid, thread_id, content):
        # Direct WebSocket/HTTP to Centrifugo
        self.centrifugo_client.publish(channel, content)
```

#### 3. The `@Agent.handler` Decorator (Auto-Runs)

```python
class Agent:
    _registered_handler = None
    
    @classmethod
    def handler(cls, func):
        """Register AND auto-run the agent handler."""
        cls._registered_handler = func
        
        # Auto-run when module is executed directly
        if __name__ == "__main__" or cls._should_auto_run():
            cls._run()
        
        return func
    
    @classmethod
    async def _execute_handler(cls, data: ChatMessage):
        """Execute with auto-detected streaming backend."""
        # OrcaHandler now uses SmartStreamClient internally
        handler = OrcaHandler()  # Auto-detects Lambda vs HTTP vs Dev
        session = handler.begin(data)
        
        try:
            await cls._registered_handler(session)
            if not session._closed:
                session.close()
        except Exception as e:
            session.error("An error occurred", exception=e)


# For Lambda: Export this at module level
def lambda_handler(event, context):
    """Auto-generated Lambda handler."""
    data = Agent._parse_event(event)
    asyncio.run(Agent._execute_handler(data))
    return {"statusCode": 200}
```

#### 3. Enhanced Session with Message Access

```python
class EnhancedSession(Session):
    """Session with direct access to message data."""
    
    @property
    def message(self) -> str:
        """The user's message."""
        return self._data.message
    
    @property
    def variables(self) -> Variables:
        """Access to variables."""
        return Variables(self._data.variables)
    
    @property
    def memory(self) -> Memory:
        """Access to user memory."""
        return self._data.memory
    
    @property
    def is_first_message(self) -> bool:
        """Whether this is the first message in conversation."""
        return self._data.first_message
```

---

### Developer Experience Comparison

#### Before (Current) - Different code for different deployments:

```python
# === FOR FASTAPI ===
from orca import OrcaHandler, ChatMessage, create_agent_app

async def process_message(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)
    try:
        session.loading.start("thinking")
        response = await call_ai(data.message)
        session.loading.end("thinking")
        session.stream(response)
        session.close()
    except Exception as e:
        session.error("Error", exception=e)

app = create_agent_app(process_message_func=process_message)  # FastAPI specific


# === FOR LAMBDA - DIFFERENT CODE ===
from orca import create_hybrid_handler, ChatMessage, OrcaHandler

async def process_message(data: ChatMessage):
    # Same logic repeated...
    handler = OrcaHandler()
    session = handler.begin(data)
    # ...

handler = create_hybrid_handler(process_message_func=process_message)  # Lambda specific
```

#### After (Proposed) - ONE file for ALL deployments:

```python
# agent.py - THE ONLY FILE YOU EVER WRITE
from orca import Agent

@Agent.handler
async def my_agent(session):
    session.loading.start("thinking")
    response = await call_ai(session.message)
    session.loading.end("thinking")
    session.stream(response)
    # Done. No close(), no try/except, no deployment code.
```

**That's it. The entire agent is 7 lines.**

Deployment is handled by environment/Docker, not code:

```bash
# Local dev
python agent.py                              # → HTTP server on :5001

# Production HTTP  
docker run -e PORT=8080 my-agent             # → HTTP server on :8080

# AWS Lambda
# Just deploy agent.py - SDK auto-detects Lambda context

# SQS Worker
docker run -e ORCA_RUNTIME=sqs my-agent      # → Polls SQS queue
```

---

### Benefits

| Benefit | Description |
|---------|-------------|
| **Zero deployment code** | Developer writes agent logic ONLY. No `create_agent_app`, no `create_hybrid_handler` |
| **Auto-detect runtime** | SDK detects Lambda, SQS, HTTP automatically via environment |
| **Auto-detect mode** | SDK detects dev (localhost) vs production (Centrifugo) automatically |
| **One file** | Entire agent is a single Python file with `@Agent.handler` |
| **Auto-lifecycle** | Session opens/closes automatically, error handling built-in |
| **Config via environment** | `PORT`, `ORCA_RUNTIME`, `CENTRIFUGO_URL` - not code |
| **Works anywhere** | Same 7 lines run on localhost, Docker, Lambda, SQS, Kubernetes |
| **Testable** | Mock `session` object for unit tests |

---

### Infrastructure Configuration (Not Code)

The deployment target is controlled by **infrastructure**, not code changes:

#### Dockerfile Examples

```dockerfile
# === HTTP Server (Default) ===
FROM python:3.11-slim
COPY agent.py .
RUN pip install orcapt-sdk
CMD ["python", "agent.py"]
# SDK auto-detects → runs HTTP server


# === SQS Worker ===
FROM python:3.11-slim
COPY agent.py .
RUN pip install orcapt-sdk
ENV ORCA_RUNTIME=sqs
ENV ORCA_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/...
CMD ["python", "agent.py"]
# SDK auto-detects → polls SQS


# === Lambda (same agent.py, no changes) ===
FROM public.ecr.aws/lambda/python:3.11
COPY agent.py .
RUN pip install orcapt-sdk
CMD ["agent.lambda_handler"]
# SDK auto-detects AWS_LAMBDA_FUNCTION_NAME → Lambda mode
```

#### Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `ORCA_RUNTIME` | `http`, `lambda`, `sqs`, `cron` | Force specific runtime (optional, auto-detected) |
| `PORT` | `5001` (default) | HTTP server port |
| `ORCA_SQS_QUEUE_URL` | URL | SQS queue to poll |
| `ORCA_DEV_MODE` | `true`/`false` | Enable dev mode (auto-detected) |
| `CENTRIFUGO_URL` | URL | Production streaming URL |
| `CENTRIFUGO_TOKEN` | token | Production streaming token |

---

### The Lambda Problem: Why SQS is Needed

**Lambda can't stream directly to Centrifugo.** Lambda is request-response - it can't hold open WebSocket connections.

```
❌ Lambda → Centrifugo (NOT POSSIBLE - no persistent connection)

✅ Lambda → SQS → Worker → Centrifugo (WORKS)
```

**But the developer shouldn't need to know this!** The SDK should handle it automatically:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer's Code (SAME)                      │
│                                                                  │
│   @Agent.handler                                                 │
│   async def my_agent(session):                                   │
│       session.stream("Hello!")  # Just works everywhere         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│      HTTP / Docker       │    │         Lambda           │
│                          │    │                          │
│  session.stream()        │    │  session.stream()        │
│       │                  │    │       │                  │
│       ▼                  │    │       ▼                  │
│  Centrifugo (direct)     │    │  SQS Queue (auto)        │
│       │                  │    │       │                  │
│       ▼                  │    │       ▼                  │
│  User sees streaming     │    │  Worker picks up         │
│                          │    │       │                  │
│                          │    │       ▼                  │
│                          │    │  Centrifugo              │
│                          │    │       │                  │
│                          │    │       ▼                  │
│                          │    │  User sees streaming     │
└──────────────────────────┘    └──────────────────────────┘
```

**The SDK auto-detects Lambda and routes through SQS automatically.** The developer's code is identical.

---

### Auto-Detection: Dev vs Production

The SDK also handles **localhost vs production** automatically:

```python
# Same code. Zero changes.
@Agent.handler
async def my_agent(session):
    session.stream("Hello!")  # Works in dev AND production
```

**Auto-detection logic:**

```
┌─────────────────────────────────────────────────────────┐
│                   SDK Auto-Detects                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CENTRIFUGO_URL exists?                                  │
│      YES → Production Mode (stream via Centrifugo)       │
│      NO  → Dev Mode (in-memory streaming, console logs)  │
│                                                          │
│  OR explicit: ORCA_DEV_MODE=true → Dev Mode              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**What this means for the developer:**

| Environment | What SDK Does | Developer Code |
|-------------|---------------|----------------|
| **Localhost** | In-memory streaming, console output, no external deps | Same |
| **Production** | Centrifugo streaming, API calls, error reporting | Same |
| **Lambda** | Lambda event parsing, async handling | Same |
| **SQS** | Queue polling, message parsing | Same |

**The developer writes ONE file. The SDK adapts to everything else.**

---

### Summary: What the Developer Experiences

```python
# agent.py - THE ONLY FILE THE DEVELOPER WRITES

from orca import Agent

@Agent.handler
async def my_agent(session):
    session.loading.start("thinking")
    response = await call_ai(session.message)
    session.loading.end("thinking")
    session.stream(response)
```

**That's it. 7 lines. Works everywhere:**

| Where | How | SDK Does |
|-------|-----|----------|
| `python agent.py` | Local dev | In-memory streaming, console |
| `docker run agent` | Production HTTP | Direct Centrifugo |
| AWS Lambda | Production | SQS → Worker → Centrifugo |
| SQS Worker | Background | Polls queue, processes |

**The developer never writes:**
- ❌ `create_agent_app()`
- ❌ `create_hybrid_handler()`
- ❌ `OrcaHandler(dev_mode=True)`
- ❌ `if runtime == "lambda": ...`
- ❌ Different code for different deployments

**The SDK handles:**
- ✅ Dev vs Production (auto-detect `CENTRIFUGO_URL`)
- ✅ HTTP vs Lambda vs SQS (auto-detect `AWS_LAMBDA_FUNCTION_NAME`)
- ✅ Lambda streaming via SQS (automatic routing)
- ✅ Session lifecycle (auto-close, error handling)
- ✅ Everything else

---

### Migration Path

1. **v1.x** - Keep current API, add `Agent` class as alternative
2. **v2.0** - Make `Agent` the primary API, deprecate old patterns
3. **v3.0** - Remove old patterns entirely

This allows gradual adoption without breaking existing code.

---

*This review was generated by an AI assistant analyzing the codebase structure, code patterns, documentation, and developer experience.*

