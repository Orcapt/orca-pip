# Lexia Dev Mode Guide

## Overview

Lexia now supports **Dev Mode** for local development without requiring Centrifugo. This makes it easier to develop and test AI agents locally.

## What is Dev Mode?

In production, Lexia uses **Centrifugo** for real-time WebSocket streaming to the frontend. In dev mode, Lexia uses:
- **In-memory storage** for streaming data
- **SSE (Server-Sent Events)** for real-time updates
- **Simple HTTP polling** as an alternative
- **Console output** for immediate visibility

## How to Enable Dev Mode

### Option 1: Direct Parameter (Recommended)

```python
from lexia import LexiaHandler

# Enable dev mode
lexia = LexiaHandler(dev_mode=True)
```

### Option 2: Environment Variable

```bash
export LEXIA_DEV_MODE=true
python main.py
```

```python
from lexia import LexiaHandler

# Will automatically detect LEXIA_DEV_MODE env var
lexia = LexiaHandler()
```

### Option 3: Command Line Argument

```python
import sys
import os

# Check for --dev flag
dev_mode = '--dev' in sys.argv

# Set environment variable
if dev_mode:
    os.environ['LEXIA_DEV_MODE'] = 'true'

from lexia import LexiaHandler

lexia = LexiaHandler()
```

Then run:
```bash
python main.py --dev
```

## How It Works

### Production Mode (Centrifugo)
```
AI Agent → Centrifugo Server → WebSocket → Frontend
```

### Dev Mode (In-Memory)
```
AI Agent → DevStreamClient (Memory) → SSE/Polling → Frontend
```

## Available Endpoints in Dev Mode

### 1. SSE Stream Endpoint
```
GET /api/v1/stream/{channel}
```

**Frontend Usage (JavaScript):**
```javascript
const eventSource = new EventSource('http://localhost:5001/api/v1/stream/your-channel-id');

eventSource.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.event) {
        case 'connected':
            console.log('Connected to stream');
            break;
        case 'delta':
            console.log('Chunk:', data.content);
            break;
        case 'complete':
            console.log('Complete response:', data.content);
            eventSource.close();
            break;
        case 'error':
            console.error('Error:', data.content);
            eventSource.close();
            break;
    }
});
```

### 2. Polling Endpoint (Alternative)
```
GET /api/v1/poll/{channel}
```

**Frontend Usage (JavaScript):**
```javascript
async function pollStream(channel) {
    const response = await fetch(`http://localhost:5001/api/v1/poll/${channel}`);
    const data = await response.json();
    
    console.log('Current state:', data);
    // data.full_response - complete response so far
    // data.finished - whether streaming is complete
    // data.chunks_count - number of chunks received
    
    if (!data.finished) {
        setTimeout(() => pollStream(channel), 100); // Poll every 100ms
    }
}
```

## Example: server-openai-example.py

```python
#!/usr/bin/env python3
import sys
import os

# Add lexia-pip to path (for local development)
LEXIA_PIP_PATH = os.path.join(os.path.dirname(__file__), '..', 'lexia-pip')
if os.path.exists(LEXIA_PIP_PATH):
    sys.path.insert(0, LEXIA_PIP_PATH)

from lexia import LexiaHandler, create_lexia_app, add_standard_endpoints

# Initialize in DEV MODE
lexia = LexiaHandler(dev_mode=True)

# Create app
app = create_lexia_app(
    title="My AI Agent",
    version="1.0.0",
    description="Dev Mode Enabled"
)

async def process_message(data):
    # Your AI logic here
    response = "Hello from dev mode!"
    
    # Stream chunks (works in both dev and production mode)
    for word in response.split():
        lexia.stream_chunk(data, word + " ")
    
    # Complete response
    lexia.complete_response(data, response)

# Add endpoints
add_standard_endpoints(app, lexia_handler=lexia, process_message_func=process_message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
```

## Benefits of Dev Mode

1. ✅ **No Centrifugo Required** - Run without external dependencies
2. ✅ **Console Output** - See streaming in real-time in terminal
3. ✅ **Easy Testing** - Test streaming locally without infrastructure
4. ✅ **Same API** - Code works in both dev and production mode
5. ✅ **Simple Frontend** - Use SSE or polling instead of WebSockets

## Console Output in Dev Mode

When dev mode is active, you'll see:
```
🔧 LexiaHandler initialized in DEV MODE (no Centrifugo)
📝 Dev stream delta added to channel-123: 15 chars
✅ Dev stream completed for channel-123
```

And the actual AI response will be printed in real-time to console.

## Production vs Dev Mode Comparison

| Feature | Production | Dev Mode |
|---------|-----------|----------|
| Streaming Protocol | Centrifugo WebSocket | SSE / Polling |
| Real-time Updates | ✅ Very Fast | ✅ Fast (100ms) |
| Console Output | ❌ No | ✅ Yes |
| External Dependencies | Centrifugo Server | None |
| Setup Complexity | Medium | Low |
| Best For | Production deployment | Local development |

## Switching Between Modes

Your code works identically in both modes:

```python
# This code works in BOTH dev and production mode
lexia.stream_chunk(data, content)
lexia.complete_response(data, full_response)
lexia.send_error(data, error_message)
```

The only difference is initialization:
```python
# Production
lexia = LexiaHandler(dev_mode=False)  # or LexiaHandler()

# Development
lexia = LexiaHandler(dev_mode=True)
```

## Troubleshooting

### Issue: Streaming not working in frontend

**Solution:** Make sure your frontend is connecting to the SSE endpoint:
```javascript
const eventSource = new EventSource(`http://localhost:5001/api/v1/stream/${channelId}`);
```

### Issue: CORS errors

**Solution:** Add CORS middleware to your FastAPI app:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Not seeing console output

**Solution:** Make sure dev mode is actually enabled:
```python
print(f"Dev mode: {lexia.dev_mode}")  # Should print: Dev mode: True
```

## Next Steps

1. Enable dev mode in your agent
2. Test locally without Centrifugo
3. Update frontend to use SSE endpoint
4. When ready for production, simply change `dev_mode=False`

That's it! Dev mode makes local development a breeze. 🚀

