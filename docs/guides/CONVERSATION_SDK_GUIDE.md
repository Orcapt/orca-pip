# Conversation SDK Guide

Guide for `OrcaConversation` in the Orca Python SDK.

## Install

```bash
pip install orca-platform-sdk-ui
```

## Initialize

### Inside an Orca agent (recommended)

```python
from orca import OrcaConversation

conv = OrcaConversation(data=data)
```

This auto-derives:
- `base_url` from `data.url` -> `<origin>/v1/external`
- auth headers from `data.headers` (`X-Workspace` / `x-workspace`)

### Standalone script

```python
from orca import OrcaConversation

conv = OrcaConversation(
    token="workspace-token",
    base_url="https://api.example.com/v1/external",
    timeout=30,
)
```

## Core Operations

### Create conversation

```python
created = conv.create(
    project_uuid="project-uuid",
    title="Support chat",
    model="gpt-4",
    user_id_external="ext-user-1",
    content="Hello!",
    force_search=False,
    active_analysis=False,
)
thread_id = created["data"]["thread_id"]
```

### Rename conversation

```python
conv.rename(thread_id=thread_id, title="Renamed chat")
```

### List messages

```python
messages = conv.list_messages(thread_id=thread_id)
```

### Send message

```python
conv.send_message(
    thread_id=thread_id,
    model="gpt-4",
    content="Follow-up question",
    is_data=False,
)
```

## Notes for current `orca-v1-api`

Verified external routes:
- `POST /v1/external/projects/{project_uuid}/conversations`
- `PUT /v1/external/conversations/{thread_id}`
- `GET /v1/external/conversations/{thread_id}/messages`
- `POST /v1/external/conversations/{thread_id}/messages`

SDK also includes `list/get/delete` helpers; those depend on backend route availability in your deployment.

## Error Handling

```python
from orca.conversation import ConversationException

try:
    conv.rename(thread_id="missing", title="x")
except ConversationException as e:
    print(e.status_code)
    print(e.response)
```
