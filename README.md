# Orca SDK

Professional Python SDK for building real-time AI agents with streaming and production-ready deployment.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🚀 **Real-time Streaming** - Stream responses to users in real-time
- 🏗️ **Clean Architecture** - SOLID principles, dependency injection, modular design
- ⚡ **AWS Lambda Ready** - Deploy to Lambda with one command
- 🎨 **Design Patterns** - Builder, middleware, context managers
- 📦 **Storage SDK** - Integrated file storage management
- 💬 **Conversation SDK** - Create, rename, and manage conversations via external API
- 🔒 **Production Ready** - Error handling, logging, type safety
- ⚙️ **Focused Core** - Lean dependency surface for core streaming and deployment

## Quick Start

### Installation

```bash
pip install orca-platform-sdk-ui
```

**Note:** The package name on PyPI is `orca-platform-sdk-ui`, but imports still use `orca`:

```python
from orca import OrcaHandler  # ✅ Correct
```

### Basic Usage

**FastAPI / Web App (Standard Factory):**

```python
from orca import create_agent_app, ChatMessage, OrcaHandler

async def process_msg(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)
    session.stream(f"Echo: {data.message}")
    session.close()

app = create_agent_app(process_message_func=process_msg)
# Run with: uvicorn main:app
```

**SessionBuilder (Queued Operations):**

```python
from orca import OrcaHandler
from orca.patterns import SessionBuilder

handler = OrcaHandler(dev_mode=True)

# All operations are queued until execute() or complete() is called
builder = SessionBuilder(handler).start_session(data)
builder.add_stream("Hello, world!")
builder.add_image("https://example.com/image.jpg")
builder.add_button("Click", "https://example.com")
builder.execute()  # Execute all queued operations
result = builder.complete()  # Execute remaining + close session
```

### Lambda Deployment

```python
from orca import create_hybrid_handler, ChatMessage, OrcaHandler

async def my_agent_logic(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)
    session.stream("Response from Lambda!")
    session.close()

# Unified handler for HTTP (FastAPI), SQS, and Cron
handler = create_hybrid_handler(process_message_func=my_agent_logic)
```

## Documentation

| Document                                                  | Description                         |
| --------------------------------------------------------- | ----------------------------------- |
| [Quick Reference](docs/guides/QUICK_REFERENCE.md)         | API reference and quick examples    |
| [Developer Guide](docs/guides/DEVELOPER_GUIDE.md)         | Complete development guide          |
| [API Reference](docs/guides/API_REFERENCE.md)             | Complete API documentation          |
| [Patterns Guide](docs/guides/PATTERNS_GUIDE.md)           | Design patterns and best practices  |
| [Utilities Guide](docs/guides/UTILITIES_GUIDE.md)         | Exceptions, decorators, and logging |
| [Storage SDK Guide](docs/guides/STORAGE_SDK_GUIDE.md)     | Storage SDK and API reference       |
| [Conversation SDK Guide](docs/guides/CONVERSATION_SDK_GUIDE.md) | Conversation management SDK   |
| [Lambda Deploy Guide](docs/guides/LAMBDA_DEPLOY_GUIDE.md) | AWS Lambda deployment guide         |
| [Dev Mode Guide](docs/guides/DEV_MODE_GUIDE.md)           | Local development setup             |
| [Contributing](CONTRIBUTING.md)                           | How to contribute                   |
| [Security](SECURITY.md)                                   | Security policies                   |
| [Changelog](CHANGELOG.md)                                 | Version history                     |

## Examples

Complete examples are available in the [`examples/`](examples/) directory:

### Quick Start

- [`basic_usage.py`](examples/basic_usage.py) - Basic streaming and buttons
- [`advanced_usage.py`](examples/advanced_usage.py) - Advanced features
- [`error_handling.py`](examples/error_handling.py) - Error handling patterns

### Deployment

- [`lambda_deployment_simple.py`](examples/lambda_deployment_simple.py) - **Production-ready Lambda template**
- [`lambda_usage_example.py`](examples/lambda_usage_example.py) - Advanced Lambda examples
- [`Dockerfile.lambda`](examples/Dockerfile.lambda) - Docker template
- [`requirements-lambda.txt`](examples/requirements-lambda.txt) - Lambda requirements

### Features

- [`patterns_example.py`](examples/patterns_example.py) - Design patterns
- [`storage_example.py`](examples/storage_example.py) - Storage SDK

## Core Features

### Streaming

```python
session.loading.start("thinking")
session.stream("Processing your request...")
session.loading.end("thinking")
session.close()
```

### Buttons

```python
session.button.link("Visit Website", "https://example.com")
session.button.action("Regenerate", "regenerate")
```

### Tracing

```python
session.tracing.begin("Processing", visibility="all")
session.tracing.append("Step 1: Analyzing...")
session.tracing.append("Step 2: Generating...")
session.tracing.end("Complete!")
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

### Error Handling

```python
try:
    # Your logic
    pass
except Exception as e:
    session.error("An error occurred", exception=e)
```

### Conversation Management

```python
from orca import OrcaConversation

# Inside an agent (auto-derives config from request)
conv = OrcaConversation(data=data)
conv.rename(thread_id=data.thread_id, title="New Title")

# Standalone
conv = OrcaConversation(token="workspace-token", base_url="https://api.example.com/v1/external")
result = conv.create(project_uuid="abc-123", title="Chat", model="gpt-4", user_id_external="user-1")
```

## Architecture

Orca SDK follows clean architecture principles with 14 distinct layers:

```
orca/
├── core/           # Core handler and session
├── domain/         # Interfaces and models
├── services/       # Business logic services
├── infrastructure/ # External clients
├── factories/      # Factory patterns
├── helpers/        # Helper utilities
├── utils/          # Utility functions
├── common/         # Cross-cutting concerns
├── patterns/       # Design patterns
├── adapters/       # Deployment adapters
├── storage/        # Storage SDK
└── conversation/   # Conversation SDK
```

## Requirements

- Python 3.8+
- `requests>=2.31.0`
- `pydantic>=2.0.0`
- `boto3>=1.34.0` (optional, for Lambda/SQS)

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/orcapt/orca-pip
cd orca-pip

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run examples
python examples/basic_usage.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=orca

# Run specific test
pytest tests/test_handler.py
```

## Deployment

### AWS Lambda

1. Copy templates:

```bash
cp examples/lambda_deployment_simple.py lambda_handler.py
cp examples/Dockerfile.lambda .
cp examples/requirements-lambda.txt .
```

2. Build image:

```bash
docker build -f Dockerfile.lambda -t my-agent:latest .
```

3. Deploy:

```bash
orca ship my-agent --image my-agent:latest --env-file .env
```

See [Lambda Deploy Guide](LAMBDA_DEPLOY_GUIDE.md) for complete instructions.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: [support@orcaolatform.ai](mailto:support@orcaolatform.ai)
- 📚 Docs: [docs.orcaplatform.ai](https://docs.orcaplatform.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/orcapt/orca-pip/issues)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Acknowledgments

Built with ❤️ by the Orca team.

---

**Made with 🚀 by [Orca](https://orcaplatform.com)**
