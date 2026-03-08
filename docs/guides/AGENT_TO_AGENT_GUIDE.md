# Agent-to-Agent Communication Guide

Complete guide to enabling communication between Orca agents, allowing one agent to ask another agent questions during a conversation.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Admin Setup](#admin-setup)
- [SDK Usage](#sdk-usage)
- [Practical Examples](#practical-examples)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [API Reference](#api-reference)

## Overview

Agent-to-agent communication lets an AI agent (Agent A) call another AI agent (Agent B) during a conversation to retrieve specialised information. The interaction works like a **tool call** — Agent A sends a question, waits for Agent B's response, and uses it to formulate its own reply to the end user.

### When to Use

- **Specialised knowledge**: Agent A handles general queries but delegates domain-specific questions (legal, medical, finance) to a specialist agent.
- **Data retrieval**: A customer-facing agent asks a back-office agent to look up internal data.
- **Multi-step workflows**: Orchestrate a pipeline where different agents handle different stages.
- **Translation / reformatting**: Ask a dedicated agent to translate or restructure content.

### How It Works

1. An admin connects Agent B to Agent A in the Orca admin panel.
2. When Agent A receives a message, the list of connected agents is included in the request payload.
3. Inside the agent code, the developer calls `session.ask_agent(slug, message)`.
4. The SDK sends a synchronous HTTP request through the Orca API to Agent B.
5. Agent B processes the question and returns its response.
6. Agent A receives the response string and can use it however it needs.

## Architecture

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│  End User │──────▶│   Agent A    │       │  Agent B │
│           │       │  (orca-pip)  │       │ (orca-pip)│
└──────────┘       └──────┬───────┘       └─────▲────┘
                          │                      │
                          │  session.ask_agent()  │
                          │                      │
                          ▼                      │
                   ┌──────────────┐              │
                   │   Orca API   │──────────────┘
                   │  (internal)  │  POST /agents/{slug}/ask
                   └──────────────┘
```

Key points:
- All communication is **routed through the Orca API**, never directly between agents.
- The API validates that Agent A is allowed to call Agent B (connection must exist).
- Agent B runs with `response_mode: sync` and `stream_mode: false` — it processes the question and returns the full response in a single HTTP call.
- A dedicated conversation with `source: agent` is created for traceability.

## Admin Setup

### 1. Connect Agents

In the Orca admin panel, open the agent you want to give the ability to call other agents:

- Go to **Agents** → select your agent → **Edit**
- In the **Agent Configuration** section, toggle **Connected Agents**
- Select the agents this agent should be able to communicate with
- Save

This works on all agent types: **Orca Agent**, **Agentic System**, and **External Agent**.

### 2. Verify the Connection

After saving, the agent's API resource will include `connected_agent_ids`. When a message is sent to this agent, the payload to `orca-pip` will contain:

```json
{
  "connected_agents": [
    {
      "slug": "legal-advisor",
      "name": "Legal Advisor",
      "description": "Specialises in contract law and compliance"
    },
    {
      "slug": "data-lookup",
      "name": "Data Lookup Agent",
      "description": "Queries internal databases"
    }
  ]
}
```

## SDK Usage

### Check Available Agents

```python
from orca import OrcaHandler, ChatMessage

async def process_msg(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    # List connected agents
    agents = session.available_agents
    for agent in agents:
        print(f"  {agent.slug}: {agent.name} — {agent.description}")

    session.stream("Processing your request...")
    session.close()
```

### Ask an Agent

```python
async def process_msg(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    # Ask a connected agent a question
    response = session.ask_agent(
        slug="legal-advisor",
        message="Is this clause enforceable under EU law: 'Non-compete for 5 years'?"
    )

    session.stream(f"According to our legal advisor: {response}")
    session.close()
```

### Method Signature

```python
session.ask_agent(
    slug: str,           # Target agent's slug (must be in connected_agents)
    message: str,        # The question to send
    timeout: int = 120   # HTTP timeout in seconds (default: 2 minutes)
) -> str                 # Returns the agent's response content
```

### Property: available_agents

```python
session.available_agents -> list[ConnectedAgent]
```

Each `ConnectedAgent` has:
- `slug: str` — The agent's unique identifier
- `name: str` — Display name
- `description: str` — What the agent does

## Practical Examples

### Example 1: Customer Support with Specialist Escalation

```python
from orca import OrcaHandler, ChatMessage, create_agent_app

async def process_msg(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    user_message = data.message.lower()

    if "legal" in user_message or "contract" in user_message:
        session.loading.start("consulting")

        legal_response = session.ask_agent(
            slug="legal-advisor",
            message=f"Customer question: {data.message}"
        )

        session.loading.end("consulting")
        session.stream(f"I consulted our legal team. Here's what they said:\n\n{legal_response}")
    else:
        session.stream(f"Thanks for your message! Here's my answer: ...")

    session.close()

app = create_agent_app(process_msg)
```

### Example 2: Multi-Agent Pipeline

```python
async def process_msg(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    session.loading.start("searching")
    raw_data = session.ask_agent("data-lookup", f"Find sales data for: {data.message}")
    session.loading.end("searching")

    session.loading.start("analyzing")
    analysis = session.ask_agent("analyst", f"Analyse this data:\n{raw_data}")
    session.loading.end("analyzing")

    session.stream(analysis)
    session.close()
```

### Example 3: Conditional Routing

```python
async def process_msg(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    # Only call agents that are actually connected
    available_slugs = [a.slug for a in session.available_agents]

    if "translate" in data.message and "translator" in available_slugs:
        translated = session.ask_agent("translator", data.message)
        session.stream(translated)
    elif "summarise" in data.message and "summariser" in available_slugs:
        summary = session.ask_agent("summariser", data.message)
        session.stream(summary)
    else:
        session.stream("I'll handle this myself.")

    session.close()
```

## Error Handling

### Agent Not Connected

If you try to call an agent that isn't in the connected list, `ask_agent` raises a `ValueError`:

```python
try:
    response = session.ask_agent("unknown-agent", "Hello")
except ValueError as e:
    # "Agent 'unknown-agent' is not connected. Available agents: ['legal-advisor']"
    session.stream("Sorry, I can't access that agent.")
    session.close()
```

### Agent Unavailable or Timeout

If the target agent is down or takes too long, `ask_agent` raises a `RuntimeError`:

```python
try:
    response = session.ask_agent("legal-advisor", "Check this contract", timeout=60)
except RuntimeError as e:
    # "Failed to get response from agent 'legal-advisor': ..."
    session.stream("The specialist agent is currently unavailable. Please try again later.")
    session.close()
```

### Full Pattern

```python
async def process_msg(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    try:
        session.loading.start("consulting")
        response = session.ask_agent("legal-advisor", data.message)
        session.loading.end("consulting")
        session.stream(response)
    except ValueError:
        session.stream("This agent doesn't have access to a legal advisor.")
    except RuntimeError:
        session.stream("The legal advisor is temporarily unavailable.")
    except Exception as e:
        session.error("Something went wrong", exception=e)
        return

    session.close()
```

## Best Practices

### 1. Always Check Availability

Before calling an agent, verify it's connected. This makes your code resilient to admin configuration changes:

```python
if "legal-advisor" in [a.slug for a in session.available_agents]:
    response = session.ask_agent("legal-advisor", question)
```

### 2. Use Loading Indicators

Agent-to-agent calls can take several seconds. Always show a loading state:

```python
session.loading.start("consulting")
response = session.ask_agent("specialist", question)
session.loading.end("consulting")
```

### 3. Set Appropriate Timeouts

The default timeout is 120 seconds. Adjust based on the target agent's expected response time:

```python
# Fast lookup agent — 30 seconds is plenty
response = session.ask_agent("data-lookup", query, timeout=30)

# Complex analysis agent — may need more time
response = session.ask_agent("deep-analyst", data, timeout=180)
```

### 4. Keep Messages Focused

Send clear, specific questions. The target agent doesn't have access to Agent A's conversation history — it only sees the message you send:

```python
# Good: specific, self-contained question
response = session.ask_agent("legal-advisor",
    "Is a 5-year non-compete clause enforceable in Germany for a software engineer?"
)

# Bad: vague, depends on context the target agent doesn't have
response = session.ask_agent("legal-advisor", "What do you think about this?")
```

### 5. Don't Chain Too Deeply

Avoid long chains of agent-to-agent calls (A → B → C → D). Each hop adds latency and increases the risk of timeouts. If you need complex orchestration, design a dedicated orchestrator agent that calls specialists in parallel where possible.

### 6. Handle Failures Gracefully

Always wrap `ask_agent` in try/except. The end user should never see a raw error — provide a fallback message.

## API Reference

### Session Methods

| Method | Description |
|--------|-------------|
| `session.available_agents` | List of `ConnectedAgent` objects available for this agent |
| `session.ask_agent(slug, message, timeout=120)` | Send a question to a connected agent and return its response |

### ConnectedAgent Model

| Field | Type | Description |
|-------|------|-------------|
| `slug` | `str` | Unique identifier for the agent |
| `name` | `str` | Display name |
| `description` | `str` | What the agent does (may be empty) |

### Errors

| Error | When |
|-------|------|
| `ValueError` | The target agent slug is not in the connected agents list |
| `RuntimeError` | The HTTP request to the target agent failed (timeout, network error, 4xx/5xx) |

### Internal API Endpoint

The SDK calls this endpoint under the hood (developers don't call it directly):

```
POST /api/internal/v1/agents/{agent_slug}/ask

Body:
{
    "message": "Your question here",
    "thread_id": "current-thread-id",
    "conversation_id": 123
}

Response:
{
    "status": "success",
    "content": "The agent's response text",
    "agent_slug": "legal-advisor",
    "conversation_id": 456
}
```
