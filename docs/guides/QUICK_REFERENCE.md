# Quick Reference

Fast reference for the current Orca Python SDK surface.

## Install

```bash
pip install orca-platform-sdk-ui
```

Package name is `orca-platform-sdk-ui`, import path is `orca`.

## FastAPI Agent (recommended)

```python
from orca import ChatMessage, OrcaHandler, create_agent_app

async def process_message(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)
    try:
        session.loading.start("thinking")
        session.stream(f"Echo: {data.message}")
        session.loading.end("thinking")
        session.close()
    except Exception as e:
        session.error("Failed to process message", exception=e)

app, handler = create_agent_app(process_message)
```

## Core Session API

```python
session = handler.begin(data)
session.stream("Hello")
session.close()
session.error("Something went wrong", exception=e)
```

## Common Operations

```python
# Loading
session.loading.start("thinking")
session.loading.end("thinking")

# Buttons
session.button.link("Docs", "https://docs.example.com", row=1, color="primary")
session.button.action("Regenerate", "regenerate", row=1)

# Media
session.image.send("https://example.com/image.jpg")
session.video.send("https://example.com/video.mp4")
session.video.youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Location / cards / audio
session.location.send_coordinates(35.6892, 51.3890)
session.card.send([{"header": "Card title", "text": "Card text"}])
session.audio.send_single("https://example.com/audio.mp3", label="Track")

# HTML / charts
session.html.send("<div>Custom HTML</div>")
session.html.send_figure(plt)
session.html.send_plotly(fig)

# Tracing and usage
session.tracing.begin("Planning", visibility="all")
session.tracing.append("Step 1 complete")
session.tracing.end("Done")
session.usage.track(tokens=1200, token_type="total", cost="0.02", label="Model run")
```

## Agent-to-Agent

```python
# Available connected agents are passed in request payload
for agent in session.available_agents:
    print(agent.slug, agent.name)

answer = session.ask_agent("legal-advisor", "Is this clause valid?", timeout=120)
session.stream(answer)
```

## Conversation SDK

```python
from orca import OrcaConversation

# Inside an agent (auto-derives base URL from data.url)
conv = OrcaConversation(data=data)
conv.rename(thread_id=data.thread_id, title="Updated title")

# Standalone
conv = OrcaConversation(
    token="workspace-token",
    base_url="https://api.example.com/v1/external",
)

created = conv.create(
    project_uuid="project-uuid",
    title="Support chat",
    model="gpt-4",
    user_id_external="ext-user-1",
    content="Hello!",
)

conv.send_message(
    thread_id=created["data"]["thread_id"],
    model="gpt-4",
    content="Follow-up",
)
```

## Storage SDK

```python
from orca import OrcaStorage

storage = OrcaStorage(
    workspace="my-workspace",
    token="workspace-token",
    base_url="https://api.example.com/v1/storage",
    mode="prod",
)

storage.create_bucket("reports")
storage.upload_file("reports", "report.pdf", folder="2026/q1")
files = storage.list_files("reports", folder="2026")
```

## Message Modes

`ChatMessage` supports per-request execution modes:

- `response_mode="async"` + `stream_mode=True` (default): background processing with real-time stream
- `response_mode="sync"` + `stream_mode=False`: wait for full content in HTTP response
- `response_mode="async"` + `stream_mode=False`: background processing with no real-time stream

## See Also

- `API_REFERENCE.md`
- `DEVELOPER_GUIDE.md`
- `CONVERSATION_SDK_GUIDE.md`
- `STORAGE_SDK_GUIDE.md`
- `AGENT_TO_AGENT_GUIDE.md`
