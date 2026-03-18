# API Reference

Current API reference for `orca-platform-sdk-ui` (`import orca`).

## Core Models

### `Variable`

```python
from orca import Variable

v = Variable(name="OPENAI_API_KEY", value="...", type="secret")
```

Fields:
- `name: str`
- `value: str`
- `id: str = ""`
- `type: str = ""`

### `ConnectedAgent`

Fields:
- `slug: str`
- `name: str`
- `description: str = ""`

### `KnowledgeStore`

Fields:
- `store_id: str`
- `name: str`
- `provider: str = "google_file_search"`

### `ChatMessage`

```python
from orca import ChatMessage
```

Common fields used by SDK operations:
- `thread_id`, `model`, `message`, `conversation_id`
- `response_uuid`, `message_uuid`, `channel`
- `variables: list[Variable]`
- `url`, `url_update`, `url_upload`
- `headers: dict[str, str] | None`
- `stream_url`, `stream_token`
- `chat_history`, `memory`
- `connected_agents`, `knowledge_stores`
- `response_mode: "sync" | "async"` (default `async`)
- `stream_mode: bool` (default `True`)

## `OrcaHandler`

```python
from orca import OrcaHandler

handler = OrcaHandler(dev_mode=False)
session = handler.begin(data)
```

Constructor:
- `OrcaHandler(dev_mode=None, stream_client=None, api_client=None, buffer_manager=None, button_renderer=None, loading_marker_provider=None, usage_tracker=None, tracing_service=None, error_handler=None, response_builder=None)`

Main methods:
- `begin(data) -> Session`
- `stream(data, content: str) -> None`
- `close(data, usage_info=None, file_url=None) -> str`
- `send_error(data, error_message: str, trace=None, exception=None) -> None`
- `update_centrifugo_config(stream_url: str, stream_token: str) -> None`

## `Session`

Created by `handler.begin(data)`.

Core methods:
- `stream(content: str) -> None`
- `close(usage_info=None, file_url=None) -> str`
- `error(error_message: str, exception=None, trace=None) -> None`
- `escalate(action="human_handoff", reason=None) -> bool`
- `ask_agent(slug: str, message: str, timeout: int = 120) -> str`

Properties:
- `loading`, `image`, `video`, `location`, `card`, `audio`, `html`
- `tracing`, `usage`, `button`, `escalation`
- `available_agents`

## Factories

### `create_agent_app`

```python
from orca import create_agent_app

app, handler = create_agent_app(
    process_message_func=my_async_handler,
    title="My Agent",
)
```

Signature:
- `create_agent_app(process_message_func, title="Orca AI Agent", version=None, description="AI agent with Orca platform integration", level=logging.INFO) -> tuple[FastAPI, OrcaHandler]`

### `create_hybrid_handler`

```python
from orca import create_hybrid_handler

handler = create_hybrid_handler(process_message_func=my_async_handler)
```

Returns a Lambda-compatible handler that routes HTTP/SQS/Cron events.

## Conversation SDK

### `OrcaConversation`

```python
from orca import OrcaConversation
```

Constructor:
- `OrcaConversation(token=None, base_url=None, data=None, timeout=30)`

Methods:
- `create(project_uuid, title, model, user_id_external, content=None, force_search=False, active_analysis=False, file=None)`
- `rename(thread_id, title)`
- `list(project_uuid, search=None, model=None, user=None)` *(depends on backend routes)*
- `get(project_uuid, thread_id)` *(depends on backend routes)*
- `delete(project_uuid, thread_id)` *(depends on backend routes)*
- `list_messages(thread_id)`
- `send_message(thread_id, content=None, model=None, force_search=None, active_analysis=None, file=None, is_data=False)`

Exception:
- `ConversationException` (status + parsed response payload)

## Storage SDK

### `OrcaStorage`

```python
from orca import OrcaStorage
```

Constructor:
- `OrcaStorage(workspace, token, base_url="http://localhost:8000/api/v1/storage", mode="dev", timeout=30)`

Bucket methods:
- `create_bucket`, `list_buckets`, `get_bucket_info`, `delete_bucket`

File methods:
- `upload_file`, `upload_buffer`, `list_files`, `download_file`
- `get_download_url`, `get_file_info`, `delete_file`

Permission methods:
- `add_permission`, `list_permissions`, `remove_permission`
