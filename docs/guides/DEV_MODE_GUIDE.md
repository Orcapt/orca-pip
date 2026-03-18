# Dev Mode Guide

Use Dev Mode to build and debug locally without Centrifugo.

## Enable Dev Mode

### Option 1: Environment variable

```bash
export ORCA_DEV_MODE=true
```

### Option 2: Constructor flag

```python
from orca import OrcaHandler

handler = OrcaHandler(dev_mode=True)
```

## What changes in Dev Mode

- Streams are handled by in-memory `DevStreamClient`
- You can consume stream events over SSE or polling endpoints
- Your agent logic stays the same (`session.stream`, `session.close`, `session.error`)

## Local FastAPI Setup

```python
from orca import ChatMessage, OrcaHandler, create_agent_app

handler = OrcaHandler(dev_mode=True)

async def process_message(data: ChatMessage):
    session = handler.begin(data)
    try:
        session.loading.start("thinking")
        session.stream(f"Dev mode: {data.message}")
        session.loading.end("thinking")
        session.close()
    except Exception as e:
        session.error("Failed", exception=e)

app, _ = create_agent_app(process_message, title="Dev Agent")
```

## Dev Endpoints

When using standard endpoints, these are available:

- `GET /api/v1/stream/{channel}` (SSE)
- `GET /api/v1/poll/{channel}` (polling fallback)
- `POST /api/v1/send_message`

### SSE client example

```javascript
const source = new EventSource("http://localhost:8000/api/v1/stream/my-channel");

source.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  if (data.event === "delta") console.log(data.content);
  if (data.event === "complete" || data.event === "error") source.close();
});
```

## Request Modes in Dev

`response_mode` and `stream_mode` still apply:

- `sync + no-stream`: returns full content in HTTP response
- `async + stream`: live stream + background processing
- `async + no-stream`: background processing only

## Common Checks

- Confirm mode: `print(handler.dev_mode)`
- Verify stream channel exists in incoming `ChatMessage.channel`
- Use `/api/v1/poll/{channel}` to inspect current stream state quickly
