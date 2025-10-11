# Version 1.2.5 Release Notes

## What's New

### Background Thread Execution in Dev Mode

Fixed streaming in dev mode to work with synchronous OpenAI code (regular `for chunk in stream` loops).

**Previous Issue (v1.2.4):**
- Dev mode used async background task
- Sync OpenAI loops blocked the event loop
- SSE couldn't flush until loop completed
- Result: Buffering, all chunks appeared at once

**Fix (v1.2.5):**
- Dev mode now runs `process_message()` in a background **thread**
- Thread has its own event loop, doesn't block main loop
- SSE generator uses async queue to receive chunks
- Result: Real-time streaming works perfectly!

## Key Benefits

✅ **No App Code Changes** - Your OpenAI code stays identical in dev/prod
✅ **True Real-Time Streaming** - SSE flushes chunks immediately
✅ **Same API** - `lexia.stream_chunk()` works in both modes
✅ **Backward Compatible** - No breaking changes

## Technical Details

### Dev Mode Flow:
```
HTTP Request
    ↓
FastAPI spawns background thread
    ↓
thread: process_message() runs with own event loop
    │   for chunk in openai_stream:
    │       lexia.stream_chunk(data, chunk)
    │           ↓
    │       DevStreamClient.queue.put(chunk)
    ↓
SSE generator: await queue.get()
    ↓
yield f"data: {chunk}\n\n" → Browser (immediate!)
```

### Production Mode Flow (Unchanged):
```
HTTP Request → Return {"status": "success"}
    ↓
Background async task: process_message()
    │   for chunk in openai_stream:
    │       lexia.stream_chunk(data, chunk)
    │           ↓
    │       CentrifugoClient.publish(chunk)
    ↓
Centrifugo → WebSocket → Frontend
```

## Example Usage

**Your code (identical in both modes):**
```python
from lexia import LexiaHandler
from openai import OpenAI

lexia = LexiaHandler(dev_mode=True)  # or False for prod

async def process_message(data):
    client = OpenAI(api_key=api_key)
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": data.message}],
        stream=True
    )
    
    # Same loop in dev and prod!
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            lexia.stream_chunk(data, content)  # Works in both!
```

## Migration from 1.2.4

No migration needed! Just upgrade:
```bash
pip install --upgrade lexia
```

Your existing code works as-is. The only difference:
- **v1.2.4**: Dev mode might buffer with sync OpenAI
- **v1.2.5**: Dev mode streams perfectly with sync OpenAI

## Files Changed

- `lexia/web/endpoints.py`: Changed dev mode to use threading instead of asyncio.create_task
- `lexia/__init__.py`: Bumped version to 1.2.5
- `setup.py`, `pyproject.toml`: Updated version

## Testing

Test with the starter kit:
```bash
python main.py --dev   # Should stream in real-time now!
```

---

**Published**: October 11, 2025  
**Version**: 1.2.5  
**PyPI**: https://pypi.org/project/lexia/1.2.5/

