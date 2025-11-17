# Usage Tracker Guide (Python)

## Overview

The `session.usage()` method makes it easy to track LLM token usage and costs. It automatically extracts the message UUID from your session data, so you don't need to pass it manually.

## How to Use

### 1. Import LexiaHandler

```python
from lexia import LexiaHandler
```

### 2. Begin a Session

Pass your request data (`data` object) to `lexia.begin()`:

```python
lexia = LexiaHandler()

def process_message(data):
    # Begin session - automatically extracts data.response_uuid
    session = lexia.begin(data)
    
    # Now you can track usage!
```

### 3. Track Your Usage

Use the `session.usage()` method for tracking tokens.

## The Method

### `session.usage(tokens, token_type, cost=None, label=None)`
One simple method for tracking any token type.

```python
# Basic usage
session.usage(150, "prompt")
session.usage(250, "completion")

# With cost
session.usage(150, "prompt", cost="0.001")
session.usage(250, "completion", cost="0.002")

# With cost and label
session.usage(50, "function_call", cost="0.04", label="DALL-E Image")
session.usage(100, "tool_usage", cost="0.002", label="Database Query")
```

### Supported Token Types

- `"prompt"` or `"input"` - Input/prompt tokens
- `"completion"` or `"output"` - Output/completion tokens
- `"function_call"` - Function calling tokens
- `"tool_usage"` - Tool usage tokens
- `"total"` - Total tokens

## Complete Example

```python
from lexia import LexiaHandler
from openai import OpenAI

lexia = LexiaHandler()

def process_message(data):
    # Begin session
    session = lexia.begin(data)
    
    try:
        # Make your OpenAI call
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        # Track the usage
        usage_info = response.usage
        
        if usage_info:
            session.usage(usage_info.prompt_tokens, "prompt")
            session.usage(usage_info.completion_tokens, "completion")
            session.usage(usage_info.total_tokens, "total")
        
        # If you call DALL-E or other functions
        image_url = generate_image(prompt)
        session.usage(50, "function_call", cost="0.04", label="DALL-E 3 Image")
        
        # Stream response
        session.stream(response.choices[0].message.content)
        
        # Close session
        session.close()
        
    except Exception as error:
        session.error(str(error))
```

## With Cost Calculation

```python
# Example: OpenAI GPT-4 pricing
PROMPT_COST_PER_1K = 0.03
COMPLETION_COST_PER_1K = 0.06

def calculate_cost(tokens, price_per_thousand):
    return f"{(tokens / 1000) * price_per_thousand:.6f}"

def process_message(data):
    session = lexia.begin(data)
    
    # ... OpenAI call ...
    
    usage_info = response.usage
    
    # Calculate costs
    prompt_cost = calculate_cost(usage_info.prompt_tokens, PROMPT_COST_PER_1K)
    completion_cost = calculate_cost(usage_info.completion_tokens, COMPLETION_COST_PER_1K)
    
    # Track with costs
    session.usage(usage_info.prompt_tokens, "prompt", cost=prompt_cost)
    session.usage(usage_info.completion_tokens, "completion", cost=completion_cost)
```

## Non-Blocking Usage (Built-in!)

Usage tracking is **automatically non-blocking**. Errors won't stop your agent:

```python
# This is safe - errors are logged but won't crash your agent
session.usage(150, "prompt")
session.usage(250, "completion")

# Even if usage tracking fails, your agent continues working
session.stream("Response continues...")
```

## Token Types

| Type            | Aliases         | Use For                           |
|-----------------|-----------------|-----------------------------------|
| `prompt`        | `input`         | Input/prompt tokens               |
| `completion`    | `output`        | Output/completion tokens          |
| `function_call` |                 | Function calling tokens           |
| `tool_usage`    |                 | External tool/API usage           |
| `total`         |                 | Total tokens for entire request   |

## Configuration

Set your API base URL via environment variable:

```bash
export LEXIA_API_BASE_URL=https://api.lexiaplatform.com
```

Or it will default to `http://localhost`.

## Key Features

✅ **Automatic UUID extraction** - Pass the `data` object, and the tracker extracts `data.response_uuid` automatically  
✅ **Simple API** - Easy-to-use methods like `track_prompt()`, `track_completion()`  
✅ **Flexible** - Track any token type with custom cost and labels  
✅ **Type conversion** - Accepts numbers or strings, converts automatically  
✅ **Comprehensive logging** - See exactly what's being sent  
✅ **Error handling** - Built-in validation and error messages  

## Quick Reference

```python
# Begin session
session = lexia.begin(data)

# Track different types (one method!)
session.usage(150, "prompt")                              # Prompt tokens
session.usage(250, "completion")                          # Completion tokens
session.usage(50, "function_call")                        # Function calls
session.usage(100, "tool_usage")                          # Tool usage
session.usage(400, "total")                               # Total tokens

# With cost
session.usage(150, "prompt", cost="0.001")

# With cost and custom label
session.usage(50, "function_call", cost="0.04", label="DALL-E Image")

# Full signature
session.usage(tokens, token_type, cost=None, label=None)
```

## Example with Flask/FastAPI

```python
from flask import Flask, request
from lexia import LexiaHandler, ChatMessage
from openai import OpenAI

app = Flask(__name__)
lexia = LexiaHandler()

@app.route('/api/v1/send_message', methods=['POST'])
def send_message():
    # Parse request
    data = ChatMessage(**request.json)
    
    # Begin session
    session = lexia.begin(data)
    
    # Process with OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=data.model,
        messages=messages
    )
    
    # Track usage (non-blocking, won't crash if it fails)
    usage_info = response.usage
    session.usage(usage_info.prompt_tokens, "prompt")
    session.usage(usage_info.completion_tokens, "completion")
    session.usage(usage_info.total_tokens, "total")
    
    # Stream and close
    session.stream(response.choices[0].message.content)
    session.close()
    
    return {"response": response.choices[0].message.content}
```

## Support

For issues or questions, see the [Usage API Documentation](USAGE_API_DOCUMENTATION.md) or contact Lexia support.

