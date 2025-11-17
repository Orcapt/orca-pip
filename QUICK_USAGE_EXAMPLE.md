# Quick Usage Example (Python)

## TL;DR

```python
from lexia import LexiaHandler

lexia = LexiaHandler()

def process_message(data):
    # 1. Begin session (automatically gets data.response_uuid)
    session = lexia.begin(data)
    
    # 2. Track tokens - that's it!
    session.usage(150, "prompt")                       # Track prompt tokens
    session.usage(250, "completion")                   # Track completion tokens
    session.usage(50, "function_call", cost="0.04")   # Track with cost
```

## Real Example

```python
from lexia import LexiaHandler
from openai import OpenAI

lexia = LexiaHandler()

def process_message(data):
    # Begin session
    session = lexia.begin(data)
    
    # Make OpenAI call
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=data.model,
        messages=messages
    )
    
    # Track the usage
    usage_info = response.usage
    
    if usage_info:
        session.usage(usage_info.prompt_tokens, "prompt")
        session.usage(usage_info.completion_tokens, "completion")
        session.usage(usage_info.total_tokens, "total")
    
    # Stream response
    session.stream(response.choices[0].message.content)
    
    # Close session
    session.close()
```

## All Token Types

```python
session = lexia.begin(data)

# Different token types
session.usage(150, "prompt")              # or "input"
session.usage(250, "completion")          # or "output"
session.usage(50, "function_call")
session.usage(100, "tool_usage")
session.usage(400, "total")

# With cost
session.usage(150, "prompt", cost="0.001")
session.usage(250, "completion", cost="0.002")

# With cost and label
session.usage(50, "function_call", cost="0.04", label="DALL-E Image")
session.usage(100, "tool_usage", cost="0.002", label="Database Query")
```

## Complete Flow

```python
from lexia import LexiaHandler
from openai import OpenAI

lexia = LexiaHandler()

def process_message(data):
    # Begin session
    session = lexia.begin(data)
    
    try:
        # Your AI logic
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=data.model,
            messages=messages
        )
        
        # Track usage
        usage_info = response.usage
        session.usage(usage_info.prompt_tokens, "prompt")
        session.usage(usage_info.completion_tokens, "completion")
        
        # Stream response
        session.stream(response.choices[0].message.content)
        
        # Close session
        session.close()
        
    except Exception as e:
        # Usage tracking errors won't stop your agent (non-blocking)
        session.error(str(e))
```

## That's it! 🎉

The session:
- ✅ Gets the message UUID from `data.response_uuid` automatically
- ✅ Converts numbers to strings for you
- ✅ Sends to the Lexia API
- ✅ Logs everything for debugging
- ✅ Non-blocking - errors won't stop your agent

You just call `session.usage(tokens, type, cost, label)`!

