# Conversation SDK Guide

Complete guide to using the Orca Conversation SDK for managing conversations via the external API.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Initialisation](#initialisation)
- [Conversation Operations](#conversation-operations)
- [Message Operations](#message-operations)
- [Error Handling](#error-handling)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)

## Overview

The Orca Conversation SDK (`OrcaConversation`) provides a Python client for the external conversation API. It allows you to create, rename, list, and delete conversations, as well as inject messages into existing conversations.

### Features

- Create new conversations in a project
- Rename (update) existing conversations
- List and search conversations with filters
- Get and delete conversations
- List messages in a conversation
- Send (inject) messages into conversations
- File attachments support

### Architecture

```
┌─────────────────┐
│   Your App /    │
│   Orca Agent    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OrcaConversation│ (Python SDK)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  External API   │ (REST - /v1/external)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orca Platform  │ (Backend)
└─────────────────┘
```

## Authentication

The external API uses a single `X-Workspace` header for authentication. The header value is a **workspace token** that identifies both the workspace and the caller.

Workspace tokens are managed through the Orca platform and must be of type `Company` (workspace). The token is validated against the `tokens` table and checked for expiry.

## Initialisation

The SDK is included with `orca`:

```bash
pip install orca-platform-sdk-ui
```

### From ChatMessage (inside an agent)

When used inside an agent processing a message, the client auto-derives the base URL from the request data and uses existing headers:

```python
from orca import OrcaConversation, ChatMessage, OrcaHandler

async def process_msg(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    # Auto-derives base_url from data.url, uses data.headers
    conv = OrcaConversation(data=data)
    conv.rename(thread_id=data.thread_id, title="Summarised Chat")

    session.stream("Conversation renamed!")
    session.close()
```

### Standalone (external script)

For standalone use outside of an agent, provide the token and base URL explicitly:

```python
from orca import OrcaConversation

conv = OrcaConversation(
    token="your-workspace-token",
    base_url="https://api.orcaplatform.ai/v1/external"
)
```

### Constructor Parameters

| Parameter  | Type            | Required | Description                                              |
| ---------- | --------------- | -------- | -------------------------------------------------------- |
| `token`    | `str`           | No*      | Workspace token (sent as `X-Workspace` header)           |
| `base_url` | `str`           | No*      | External API base URL                                    |
| `data`     | `ChatMessage`   | No*      | Request data to auto-derive config from                  |
| `timeout`  | `int`           | No       | HTTP request timeout in seconds (default: 30)            |

*At least one of `token` or `data` (with headers containing `X-Workspace`) must be provided.

## Conversation Operations

### Create a Conversation

Create a new conversation within a project:

```python
result = conv.create(
    project_uuid="abc-123-def",
    title="Customer Support Chat",
    model="gpt-4",
    user_id_external="ext-user-42",
    content="Hello, I need help with my account",  # optional first message
    force_search=True,                               # optional
    active_analysis=False,                           # optional
)

print(f"Thread ID: {result['data']['thread_id']}")
```

**Parameters:**

| Parameter          | Type   | Required | Description                                     |
| ------------------ | ------ | -------- | ----------------------------------------------- |
| `project_uuid`     | `str`  | Yes      | UUID of the project                             |
| `title`            | `str`  | Yes      | Conversation title                              |
| `model`            | `str`  | Yes      | AI model identifier (e.g. `gpt-4`)             |
| `user_id_external`  | `str`  | Yes      | External user ID (`users.external_id`)          |
| `content`          | `str`  | No       | Initial user message                            |
| `force_search`     | `bool` | No       | Force knowledge-base search (default: `False`)  |
| `active_analysis`  | `bool` | No       | Enable active analysis (default: `False`)       |
| `file`             | file   | No       | File attachment (file-like object)              |

### Rename a Conversation

Update the title of an existing conversation:

```python
conv.rename(thread_id="abc-thread-id", title="Renamed Conversation")
```

### List Conversations

List conversations in a project with optional filters:

```python
# List all
result = conv.list(project_uuid="abc-123-def")

# With filters
result = conv.list(
    project_uuid="abc-123-def",
    search="support",   # filter by title (partial match)
    model="gpt-4",      # filter by model
    user="John",         # filter by user name
)

for item in result['data']:
    print(f"{item['title']} - {item['model']}")
```

### Get a Conversation

Retrieve a single conversation:

```python
result = conv.get(
    project_uuid="abc-123-def",
    thread_id="abc-thread-id"
)
print(f"Title: {result['data']['title']}")
```

### Delete a Conversation

```python
conv.delete(
    project_uuid="abc-123-def",
    thread_id="abc-thread-id"
)
```

## Message Operations

### List Messages

Get all messages in a conversation:

```python
result = conv.list_messages(thread_id="abc-thread-id")

for msg in result['data']['messages']:
    print(f"[{msg['role']}] {msg['content'][:80]}...")
```

### Send a Message

Inject a message into an existing conversation and trigger an AI response:

```python
result = conv.send_message(
    thread_id="abc-thread-id",
    content="Can you help me reset my password?",
    model="gpt-4",          # optional model override
    force_search=True,       # optional
)

print(f"Message UUID: {result['data']['message']['uuid']}")
```

### Send a Message with File

```python
with open("document.pdf", "rb") as f:
    result = conv.send_message(
        thread_id="abc-thread-id",
        content="Please analyse this document",
        file=f,
    )
```

## Error Handling

```python
from orca import OrcaConversation
from orca.conversation import ConversationException

conv = OrcaConversation(token="...", base_url="...")

try:
    result = conv.create(
        project_uuid="abc-123",
        title="Chat",
        model="gpt-4",
        user_id_external="user-1",
    )
except ConversationException as e:
    print(f"Error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")
```

### Common Error Codes

| Status | Meaning                                              |
| ------ | ---------------------------------------------------- |
| 401    | Missing or invalid workspace token                   |
| 403    | Token is not a workspace token / conversation access  |
| 404    | Project or conversation not found                    |
| 422    | Validation error (missing required fields)           |

## API Reference

### OrcaConversation

```python
class OrcaConversation:
    def __init__(
        self,
        token: str = None,
        base_url: str = None,
        data: Any = None,
        timeout: int = 30
    )
```

### Conversation Methods

| Method                                                    | Description                      |
| --------------------------------------------------------- | -------------------------------- |
| `create(project_uuid, title, model, user_id_external, ...)` | Create a new conversation     |
| `rename(thread_id, title)`                                | Rename a conversation            |
| `list(project_uuid, search?, model?, user?)`              | List conversations with filters  |
| `get(project_uuid, thread_id)`                            | Get a single conversation        |
| `delete(project_uuid, thread_id)`                         | Delete a conversation            |

### Message Methods

| Method                                                    | Description                       |
| --------------------------------------------------------- | --------------------------------- |
| `list_messages(thread_id)`                                | List all messages in conversation |
| `send_message(thread_id, content?, model?, ..., is_data?)` | Send/inject a message            |

## Best Practices

### 1. Use Inside Agents When Possible

```python
# Let the SDK auto-derive config from the request
conv = OrcaConversation(data=data)
```

### 2. Handle Errors Gracefully

```python
try:
    conv.rename(thread_id=tid, title="New Title")
except ConversationException as e:
    if e.status_code == 404:
        print("Conversation not found")
    else:
        raise
```

### 3. Reuse the Client

```python
# Create once, reuse for multiple operations
conv = OrcaConversation(token="...", base_url="...")

for project in projects:
    conversations = conv.list(project_uuid=project["uuid"])
    # ...
```

## See Also

- [Developer Guide](DEVELOPER_GUIDE.md) - Complete development guide
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Storage SDK Guide](STORAGE_SDK_GUIDE.md) - Storage operations
- [Quick Reference](QUICK_REFERENCE.md) - Quick examples
