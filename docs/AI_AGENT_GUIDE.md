# AI Agent Integration Guide for Orca SDK

> **Purpose**: This document is designed for AI coding assistants (Claude, Cursor, Copilot, etc.) to help users build, test, and deploy AI agents on the Orca platform. Follow this guide step-by-step to get users from zero to production.

---

## Table of Contents

1. [Quick Context](#quick-context)
2. [Phase 1: Dev Mode (Local Development)](#phase-1-dev-mode-local-development)
3. [Phase 2: Production Mode (Centrifugo)](#phase-2-production-mode-centrifugo)
4. [Phase 3: Lambda Deployment](#phase-3-lambda-deployment)
5. [Core Patterns & Templates](#core-patterns--templates)
6. [Session API Reference](#session-api-reference)
7. [Common Integration Patterns](#common-integration-patterns)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Complete Code Templates](#complete-code-templates)

---

## Quick Context

### What is Orca SDK?

Orca SDK (`orcapt-sdk` on PyPI, imported as `orca`) enables developers to build AI agents that:
- Stream responses in real-time to users
- Communicate with the Orca platform backend
- Handle errors, logging, and usage tracking
- Deploy to AWS Lambda with minimal configuration

### Key Principle

**Your code works identically in dev and production modes!** The only difference is initialization:

```python
# Dev mode (local testing, no external dependencies)
orca = OrcaHandler(dev_mode=True)

# Production mode (uses Centrifugo for real-time streaming)
orca = OrcaHandler(dev_mode=False)
```

### Installation

```bash
# Package name on PyPI is orcapt-sdk
pip install orcapt-sdk

# With web framework support (FastAPI)
pip install orcapt-sdk[web]
```

```python
# Import always uses 'orca'
from orca import OrcaHandler, ChatMessage
```

---

## Phase 1: Dev Mode (Local Development)

**Goal**: Get a working AI agent running locally in under 5 minutes.

### Step 1.1: Create Project Structure

```
my-agent/
├── main.py              # Main application file
├── requirements.txt     # Dependencies
└── .env                 # Environment variables (optional)
```

### Step 1.2: Install Dependencies

```bash
pip install orcapt-sdk[web] openai  # or anthropic, etc.
```

### Step 1.3: Create Basic Agent (Fastest Start)

**Option A: Using Factory (Recommended for beginners)**

```python
# main.py - Simplest possible agent
from orca import create_agent_app, ChatMessage, OrcaHandler

async def process_message(data: ChatMessage):
    """Your AI agent logic goes here."""
    handler = OrcaHandler(dev_mode=True)
    session = handler.begin(data)
    
    try:
        # Show loading indicator
        session.loading.start("thinking")
        
        # Your AI processing here
        response = f"You said: {data.message}"
        
        # Hide loading and stream response
        session.loading.end("thinking")
        session.stream(response)
        
        # Complete the response
        session.close()
        
    except Exception as e:
        session.error("An error occurred", exception=e)

# Create FastAPI app with all endpoints configured
app, orca = create_agent_app(
    process_message_func=process_message,
    title="My AI Agent",
    version="1.0.0"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Option B: Manual FastAPI Setup (More control)**

```python
# main.py - Manual setup with full control
from fastapi import FastAPI
from orca import OrcaHandler, ChatMessage, create_orca_app, add_standard_endpoints

# Initialize handler in dev mode
orca = OrcaHandler(dev_mode=True)

# Create FastAPI app
app = create_orca_app(title="My AI Agent", version="1.0.0")

async def process_message(data: ChatMessage):
    session = orca.begin(data)
    
    try:
        session.loading.start("thinking")
        
        # Your logic here
        session.stream(f"Echo: {data.message}")
        
        session.loading.end("thinking")
        session.close()
        
    except Exception as e:
        session.error("Error processing request", exception=e)

# Add standard Orca endpoints
add_standard_endpoints(app, orca_handler=orca, process_message_func=process_message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 1.4: Run the Agent

```bash
python main.py
```

You should see:
```
🔧 OrcaHandler initialized in DEV MODE (no Centrifugo)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 1.5: Test the Agent

```bash
curl -X POST http://localhost:8000/api/v1/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello AI!",
    "thread_id": "test-123",
    "model": "gpt-4",
    "conversation_id": 1,
    "response_uuid": "resp-123",
    "message_uuid": "msg-123",
    "channel": "test-channel",
    "variables": [],
    "url": "http://localhost:8000/api/callback"
  }'
```

### Step 1.6: Enable Dev Mode Options

```python
# Option 1: Direct parameter
orca = OrcaHandler(dev_mode=True)

# Option 2: Environment variable
import os
os.environ["ORCA_DEV_MODE"] = "true"
orca = OrcaHandler()  # Auto-detects

# Option 3: Command line check
import sys
if "--dev" in sys.argv:
    os.environ["ORCA_DEV_MODE"] = "true"
```

### Dev Mode Features

| Feature | Description |
|---------|-------------|
| In-memory streaming | No Centrifugo server required |
| Console output | Real-time streaming visible in terminal |
| SSE endpoint | `/api/v1/stream/{channel}` for frontend |
| Polling endpoint | `/api/v1/poll/{channel}` alternative |

### Dev Mode Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/v1/health` | GET | Detailed health status |
| `/api/v1/send_message` | POST | Main chat endpoint |
| `/api/v1/stream/{channel}` | GET | SSE streaming |
| `/api/v1/poll/{channel}` | GET | Polling alternative |
| `/docs` | GET | API documentation |

---

## Phase 2: Production Mode (Centrifugo)

**Goal**: Deploy with real-time WebSocket streaming via Centrifugo.

### Step 2.1: Switch to Production Mode

```python
# Simply change dev_mode to False (or remove the parameter)
orca = OrcaHandler(dev_mode=False)

# Or use environment variable
# export ORCA_DEV_MODE=false
orca = OrcaHandler()
```

### Step 2.2: Configure Centrifugo

The Orca platform provides Centrifugo credentials in the `ChatMessage`:

```python
async def process_message(data: ChatMessage):
    # Centrifugo config is automatically extracted from data
    # data.stream_url - Centrifugo server URL
    # data.stream_token - Authentication token
    
    session = orca.begin(data)  # Auto-configures Centrifugo
    # ... rest of your code
```

### Step 2.3: Production Flow

```
User → Orca Platform → Your Agent → OrcaHandler
                                          ↓
                                    Centrifugo ← WebSocket ← User's Browser
                                          ↓
                                    Orca Backend API
```

### Step 2.4: Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t my-agent .
docker run -p 8000:8000 my-agent
```

---

## Phase 3: Lambda Deployment

**Goal**: Deploy to AWS Lambda with SQS support for async processing.

### Step 3.1: Create Lambda Handler

**Simplest approach using `create_hybrid_handler`:**

```python
# lambda_handler.py
from orca import create_hybrid_handler, ChatMessage, OrcaHandler

async def process_message(data: ChatMessage):
    """Your agent logic - identical to local development!"""
    handler = OrcaHandler(dev_mode=False)
    session = handler.begin(data)
    
    try:
        session.loading.start("thinking")
        
        # Your AI logic here
        response = f"Lambda Agent received: {data.message}"
        
        session.loading.end("thinking")
        session.stream(response)
        session.close()
        
    except Exception as e:
        session.error("Processing failed", exception=e)

# This single handler supports:
# - HTTP requests (API Gateway / Function URL)
# - SQS messages (async processing)
# - Scheduled events (cron jobs)
handler = create_hybrid_handler(
    process_message_func=process_message,
    app_title="My Lambda Agent"
)
```

### Step 3.2: Create Dockerfile for Lambda

```dockerfile
# Dockerfile.lambda
FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements-lambda.txt .
RUN pip install --no-cache-dir -r requirements-lambda.txt

COPY lambda_handler.py .
COPY . .

CMD ["lambda_handler.handler"]
```

### Step 3.3: Create Requirements File

```txt
# requirements-lambda.txt
orcapt-sdk>=1.0.5
boto3>=1.34.0
fastapi>=0.104.0
mangum>=0.17.0

# Your AI providers
openai>=1.0.0
# anthropic>=0.7.0
```

### Step 3.4: Environment Variables

Create `.env.lambda` (never commit this file):

```bash
OPENAI_API_KEY=sk-...
STREAM_URL=https://centrifugo.yourplatform.com
STREAM_TOKEN=your-token
LOG_LEVEL=info
# SQS_QUEUE_URL is set automatically by orcapt ship
```

### Step 3.5: Build and Deploy

```bash
# Build Docker image
docker build -f Dockerfile.lambda -t my-agent:latest .

# Deploy using Orca CLI
orcapt ship my-agent \
  --image my-agent:latest \
  --memory 2048 \
  --timeout 300 \
  --env-file .env.lambda
```

### Step 3.6: Test Lambda Locally

Create `simulate_lambda.py`:

```python
import os
os.environ["ORCA_DEV_MODE"] = "true"

from orca import simulate_lambda_handler
from lambda_handler import handler

if __name__ == "__main__":
    simulate_lambda_handler(handler, message="Test message!")
```

```bash
python simulate_lambda.py
```

### Lambda Architecture

```
HTTP Request → API Gateway/Function URL → Lambda
                                             ↓
                                    create_hybrid_handler
                                             ↓
                              ┌──────────────┼──────────────┐
                              ↓              ↓              ↓
                            HTTP           SQS           Cron
                              ↓              ↓              ↓
                         FastAPI +      Direct       Scheduled
                          Mangum       Process        Handler
```

### SQS Offloading (Automatic)

When `SQS_QUEUE_URL` is set, HTTP requests automatically queue to SQS:

```
POST /api/v1/send_message
    → Validates request
    → Queues to SQS
    → Returns {"status": "queued", "response_uuid": "..."}
    
SQS Trigger → Lambda
    → Processes message
    → Streams to Centrifugo
```

---

## Core Patterns & Templates

### The Session Pattern (Always Use This)

```python
async def process_message(data: ChatMessage):
    session = orca.begin(data)  # Always start with begin()
    
    try:
        # Your processing logic
        session.stream("Response text")
        session.close()  # Always call close()
        
    except Exception as e:
        session.error("Error message", exception=e)  # Handle errors
```

### With OpenAI Integration

```python
from openai import OpenAI
from orca import OrcaHandler, ChatMessage, Variables

orca = OrcaHandler()

async def process_message(data: ChatMessage):
    session = orca.begin(data)
    
    try:
        # Get API key from variables
        vars = Variables(data.variables)
        api_key = vars.get("OPENAI_API_KEY")
        
        if not api_key:
            session.error("OPENAI_API_KEY not configured")
            return
        
        # Initialize OpenAI
        client = OpenAI(api_key=api_key)
        
        # Show loading
        session.loading.start("thinking")
        
        # Stream from OpenAI
        stream = client.chat.completions.create(
            model=data.model or "gpt-4",
            messages=[{"role": "user", "content": data.message}],
            stream=True
        )
        
        session.loading.end("thinking")
        
        # Stream chunks to user
        for chunk in stream:
            if chunk.choices[0].delta.content:
                session.stream(chunk.choices[0].delta.content)
        
        # Complete
        session.close()
        
    except Exception as e:
        session.error(f"OpenAI error: {str(e)}", exception=e)
```

### With Anthropic Integration

```python
from anthropic import Anthropic
from orca import OrcaHandler, ChatMessage, Variables

orca = OrcaHandler()

async def process_message(data: ChatMessage):
    session = orca.begin(data)
    
    try:
        vars = Variables(data.variables)
        api_key = vars.get("ANTHROPIC_API_KEY")
        
        if not api_key:
            session.error("ANTHROPIC_API_KEY not configured")
            return
        
        client = Anthropic(api_key=api_key)
        
        session.loading.start("thinking")
        
        # Stream from Claude
        with client.messages.stream(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[{"role": "user", "content": data.message}]
        ) as stream:
            session.loading.end("thinking")
            for text in stream.text_stream:
                session.stream(text)
        
        session.close()
        
    except Exception as e:
        session.error(f"Anthropic error: {str(e)}", exception=e)
```

### With User Memory

```python
from orca import OrcaHandler, ChatMessage, MemoryHelper

async def process_message(data: ChatMessage):
    session = orca.begin(data)
    
    try:
        memory = MemoryHelper(data.memory)
        
        # Personalized greeting
        if memory.has_name():
            greeting = f"Hello, {memory.get_name()}!"
        else:
            greeting = "Hello!"
        
        # Build context from memory
        context = []
        if memory.has_goals():
            context.append(f"User goals: {', '.join(memory.get_goals())}")
        if memory.has_interests():
            context.append(f"Interests: {', '.join(memory.get_interests())}")
        
        session.stream(greeting)
        if context:
            session.stream(f"\n\nI remember: {'; '.join(context)}")
        
        session.close()
        
    except Exception as e:
        session.error("Memory error", exception=e)
```

### Multi-Provider Support

```python
async def process_message(data: ChatMessage):
    session = orca.begin(data)
    vars = Variables(data.variables)
    
    try:
        model = data.model.lower()
        
        if "gpt" in model:
            response = await call_openai(vars, data)
        elif "claude" in model:
            response = await call_anthropic(vars, data)
        elif "gemini" in model:
            response = await call_gemini(vars, data)
        else:
            session.error(f"Unsupported model: {data.model}")
            return
        
        session.stream(response)
        session.close()
        
    except Exception as e:
        session.error("Processing failed", exception=e)
```

---

## Session API Reference

### Starting a Session

```python
session = orca.begin(data)  # data is ChatMessage
```

### Streaming Content

```python
session.stream("Text to stream")  # Stream text chunks
session.stream("More text...")    # Can call multiple times
```

### Closing Session

```python
# Basic close
session.close()

# With usage info
session.close(usage_info={
    'prompt_tokens': 100,
    'completion_tokens': 50,
    'total_tokens': 150
})

# Returns full aggregated response
full_text = session.close()
```

### Error Handling

```python
session.error("User-facing error message")
session.error("Error with details", exception=e)
session.error("Error with trace", trace=traceback.format_exc())
```

### Loading Indicators

```python
session.loading.start("thinking")   # Start loading
session.loading.end("thinking")     # Stop loading

# Available types: "thinking", "image", "code", "search"
session.loading.start("image")
session.loading.end("image")
```

### Media Operations

```python
# Images
session.image.send("https://example.com/image.jpg")

# Videos
session.video.send("https://example.com/video.mp4")
session.video.youtube("https://youtube.com/watch?v=...")

# Audio
session.audio.send([
    {"url": "https://example.com/audio.mp3", "label": "Track 1"}
])
session.audio.send_single("https://example.com/audio.mp3", label="Track")

# Location
session.location.send("35.6892, 51.3890")
session.location.send_coordinates(35.6892, 51.3890)

# Cards
session.card.send([
    {"photo": "url", "header": "Title", "subheader": "Sub", "text": "Content"}
])
```

### Buttons

```python
# Link button (opens URL)
session.button.link("Click Here", "https://example.com")
session.button.link("Docs", "https://docs.example.com", color="primary")

# Action button (triggers action)
session.button.action("Regenerate", "regenerate")
session.button.action("Delete", "delete", color="danger")
```

### Tracing

```python
session.tracing.begin("Step name", visibility="all")
session.tracing.append("Step progress...")
session.tracing.end("Completed")
```

### Usage Tracking

```python
session.usage.track(
    tokens=1500,
    token_type="gpt4",
    cost="0.03",
    label="OpenAI GPT-4"
)
```

---

## Common Integration Patterns

### Variables Helper

```python
from orca import Variables

vars = Variables(data.variables)

# Get variable (returns None if not found)
api_key = vars.get("OPENAI_API_KEY")

# Check if exists
if vars.has("CUSTOM_VAR"):
    value = vars.get("CUSTOM_VAR")

# List all available
print(vars.list_names())  # ['VAR1', 'VAR2', ...]

# Convert to dict
all_vars = vars.to_dict()  # {'VAR1': 'value1', ...}
```

### Memory Helper

```python
from orca import MemoryHelper

memory = MemoryHelper(data.memory)

# Get user info
name = memory.get_name()
goals = memory.get_goals()  # List[str]
location = memory.get_location()
interests = memory.get_interests()  # List[str]
preferences = memory.get_preferences()  # List[str]
experiences = memory.get_past_experiences()  # List[str]

# Check availability
if memory.has_name():
    print(f"Hello, {memory.get_name()}!")

# Check if empty
if memory.is_empty():
    print("New user")
```

### File Processing

```python
async def process_message(data: ChatMessage):
    session = orca.begin(data)
    
    try:
        # Check if file was uploaded
        if data.file_url:
            # Process file based on type
            if data.file_type == "pdf":
                content = await process_pdf(data.file_url)
            elif data.file_type == "txt":
                content = await fetch_text(data.file_url)
            else:
                content = f"Uploaded file: {data.file_type}"
            
            session.stream(f"Processed file:\n{content}")
        else:
            session.stream(f"Message: {data.message}")
        
        session.close()
        
    except Exception as e:
        session.error("File processing error", exception=e)
```

### Image Generation

```python
async def process_message(data: ChatMessage):
    session = orca.begin(data)
    
    try:
        vars = Variables(data.variables)
        client = OpenAI(api_key=vars.get("OPENAI_API_KEY"))
        
        # Show image loading
        session.loading.start("image")
        
        # Generate image
        response = client.images.generate(
            model="dall-e-3",
            prompt=data.message,
            size="1024x1024"
        )
        
        session.loading.end("image")
        
        # Send image
        session.image.send(response.data[0].url)
        session.stream(f"\n\nGenerated image for: {data.message}")
        
        session.close()
        
    except Exception as e:
        session.error("Image generation failed", exception=e)
```

---

## Troubleshooting Guide

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: orca` | Package not installed | `pip install orcapt-sdk` |
| `ModuleNotFoundError: fastapi` | Web deps missing | `pip install orcapt-sdk[web]` |
| Variables returning None | Wrong variable name | Check `vars.list_names()` |
| Streaming not working | Wrong mode or endpoint | Verify dev_mode and SSE endpoint |
| CORS errors | Missing middleware | Add CORS middleware to FastAPI |
| Lambda timeout | Processing too slow | Increase timeout or use SQS |

### Debug Checklist

```python
# 1. Verify dev mode
print(f"Dev mode: {orca.dev_mode}")

# 2. Check available variables
vars = Variables(data.variables)
print(f"Variables: {vars.list_names()}")

# 3. Check memory
memory = MemoryHelper(data.memory)
print(f"Memory empty: {memory.is_empty()}")

# 4. Enable debug logging
from orca import setup_logging
import logging
setup_logging(level=logging.DEBUG)
```

### Adding CORS (for web frontends)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Lambda-Specific Issues

| Issue | Solution |
|-------|----------|
| Event loop errors | Use `create_hybrid_handler` (handles this) |
| Cold start slow | Reduce dependencies, increase memory |
| SQS not triggering | Check event source mapping |
| 403 from Function URL | Redeploy with `orcapt ship` |

---

## Complete Code Templates

### Template 1: Minimal Dev Agent

```python
"""Minimal agent for local development."""
from orca import create_agent_app, ChatMessage, OrcaHandler

async def process_message(data: ChatMessage):
    handler = OrcaHandler(dev_mode=True)
    session = handler.begin(data)
    
    try:
        session.stream(f"Echo: {data.message}")
        session.close()
    except Exception as e:
        session.error("Error", exception=e)

app, orca = create_agent_app(process_message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Template 2: Full-Featured Agent

```python
"""Full-featured agent with all capabilities."""
import asyncio
from openai import OpenAI
from orca import (
    OrcaHandler, ChatMessage, Variables, MemoryHelper,
    create_orca_app, add_standard_endpoints, setup_logging
)
import logging

setup_logging(level=logging.INFO)
orca = OrcaHandler(dev_mode=True)
app = create_orca_app(title="Full Agent", version="1.0.0")

async def process_message(data: ChatMessage):
    session = orca.begin(data)
    vars = Variables(data.variables)
    memory = MemoryHelper(data.memory)
    
    try:
        # Personalized greeting
        greeting = f"Hello, {memory.get_name()}!" if memory.has_name() else "Hello!"
        session.stream(greeting + "\n\n")
        
        # Get API key
        api_key = vars.get("OPENAI_API_KEY")
        if not api_key:
            session.error("OPENAI_API_KEY required")
            return
        
        # Process with OpenAI
        session.loading.start("thinking")
        
        client = OpenAI(api_key=api_key)
        stream = client.chat.completions.create(
            model=data.model or "gpt-4",
            messages=[{"role": "user", "content": data.message}],
            stream=True
        )
        
        session.loading.end("thinking")
        
        # Stream response
        for chunk in stream:
            if chunk.choices[0].delta.content:
                session.stream(chunk.choices[0].delta.content)
        
        # Add buttons
        session.button.action("Regenerate", "regenerate")
        session.button.link("Learn More", "https://docs.example.com")
        
        session.close()
        
    except Exception as e:
        session.error(f"Processing failed: {str(e)}", exception=e)

add_standard_endpoints(app, orca, process_message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Template 3: Production Lambda Handler

```python
"""Production-ready Lambda handler."""
import logging
from openai import OpenAI
from orca import create_hybrid_handler, ChatMessage, OrcaHandler, Variables

async def process_message(data: ChatMessage):
    """Production agent logic."""
    handler = OrcaHandler(dev_mode=False)
    session = handler.begin(data)
    vars = Variables(data.variables)
    
    try:
        api_key = vars.get("OPENAI_API_KEY")
        if not api_key:
            session.error("API key not configured")
            return
        
        session.loading.start("thinking")
        
        client = OpenAI(api_key=api_key)
        
        # Build messages with system prompt
        messages = [
            {"role": "system", "content": data.system_message or "You are a helpful assistant."},
            {"role": "user", "content": data.message}
        ]
        
        stream = client.chat.completions.create(
            model=data.model or "gpt-4",
            messages=messages,
            stream=True
        )
        
        session.loading.end("thinking")
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                session.stream(chunk.choices[0].delta.content)
        
        session.close()
        
    except Exception as e:
        logging.error(f"Error: {e}")
        session.error("Processing failed", exception=e)

# Single handler for HTTP, SQS, and Cron
handler = create_hybrid_handler(
    process_message_func=process_message,
    app_title="Production Agent",
    level=logging.INFO
)
```

### Template 4: Multi-Step Agent with Tracing

```python
"""Agent with tracing and multi-step processing."""
from orca import OrcaHandler, ChatMessage, Variables

orca = OrcaHandler(dev_mode=True)

async def process_message(data: ChatMessage):
    session = orca.begin(data)
    
    try:
        # Step 1: Analysis
        session.tracing.begin("Analyzing request", visibility="all")
        session.loading.start("thinking")
        
        analysis = analyze_request(data.message)
        session.tracing.append(f"Found {len(analysis['entities'])} entities")
        session.tracing.end("Analysis complete")
        
        session.loading.end("thinking")
        
        # Step 2: Processing
        session.tracing.begin("Processing", visibility="all")
        
        result = process_data(analysis)
        session.tracing.append(f"Processed in {result['time_ms']}ms")
        session.tracing.end("Processing complete")
        
        # Step 3: Response
        session.stream(result['response'])
        
        # Track usage
        session.usage.track(
            tokens=result['tokens'],
            token_type="gpt4",
            cost=result['cost']
        )
        
        session.close()
        
    except Exception as e:
        session.error("Multi-step processing failed", exception=e)
```

---

## Quick Checklist

### Before Development
- [ ] Install: `pip install orcapt-sdk[web]`
- [ ] Create `main.py` with basic handler
- [ ] Test with dev mode: `OrcaHandler(dev_mode=True)`

### Before Production
- [ ] Switch to production mode: `OrcaHandler(dev_mode=False)`
- [ ] Configure proper error handling
- [ ] Add CORS middleware if needed
- [ ] Test all endpoints

### Before Lambda Deploy
- [ ] Create `lambda_handler.py` with `create_hybrid_handler`
- [ ] Create `Dockerfile.lambda`
- [ ] Create `requirements-lambda.txt`
- [ ] Create `.env.lambda` (never commit!)
- [ ] Build Docker image
- [ ] Deploy with `orcapt ship`
- [ ] Test with `simulate_lambda_handler`

---

## Summary

| Mode | Use Case | Command |
|------|----------|---------|
| Dev Mode | Local testing | `OrcaHandler(dev_mode=True)` |
| Production | Live deployment | `OrcaHandler(dev_mode=False)` |
| Lambda | AWS serverless | `create_hybrid_handler(...)` |

**Key Points:**
1. Your code works the same in all modes
2. Always use the Session pattern: `begin()` → `stream()` → `close()`
3. Always handle errors with `session.error()`
4. Use factories (`create_agent_app`, `create_hybrid_handler`) for fastest setup
5. Test locally with `simulate_lambda_handler` before deploying

---

*This guide is designed for AI coding assistants. For human-readable documentation, see the [Developer Guide](guides/DEVELOPER_GUIDE.md).*

