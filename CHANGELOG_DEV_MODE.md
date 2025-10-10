# Changelog - Dev Mode Feature

## Version 1.2.2 - Dev Mode Support

### 🎉 New Feature: Development Mode

Added complete dev mode support for local development without Centrifugo.

### What's New

#### 1. DevStreamClient (`lexia/dev_stream_client.py`)
- In-memory streaming client for development
- Thread-safe class-level storage
- Same interface as CentrifugoClient
- Automatic console output for debugging

#### 2. LexiaHandler Dev Mode Support
- New `dev_mode` parameter in constructor
- Automatic detection via `LEXIA_DEV_MODE` environment variable
- Seamlessly switches between Centrifugo and DevStreamClient
- Zero code changes needed between dev and production

#### 3. New API Endpoints
- `GET /api/v1/stream/{channel}` - SSE streaming endpoint
- `GET /api/v1/poll/{channel}` - Simple polling endpoint
- Both work with DevStreamClient in dev mode

#### 4. Documentation
- `DEV_MODE_GUIDE.md` - Complete usage guide
- `USAGE_EXAMPLE.md` - Frontend integration examples
- `DEV_MODE_IMPLEMENTATION.md` - Technical implementation details

### Usage

```python
from lexia import LexiaHandler

# Development mode
lexia = LexiaHandler(dev_mode=True)

# Production mode
lexia = LexiaHandler(dev_mode=False)

# Same code works in both!
lexia.stream_chunk(data, content)
lexia.complete_response(data, response)
```

### Benefits

- ✅ No Centrifugo server required for local dev
- ✅ Real-time console output
- ✅ SSE and polling support for frontend
- ✅ Identical API in dev and production
- ✅ Easy local testing and debugging
- ✅ Zero infrastructure setup

### Breaking Changes

None - fully backwards compatible!

### Migration Guide

No migration needed. Dev mode is opt-in:

```python
# Old code (still works)
lexia = LexiaHandler()

# New code (with dev mode)
lexia = LexiaHandler(dev_mode=True)
```

### Files Added/Modified

**Added:**
- `lexia/dev_stream_client.py`
- `DEV_MODE_GUIDE.md`
- `CHANGELOG_DEV_MODE.md`

**Modified:**
- `lexia/unified_handler.py` - Added dev mode support
- `lexia/__init__.py` - Export DevStreamClient
- `lexia/web/endpoints.py` - Added SSE endpoints

**Examples Updated:**
- `lexia-frondend-python-dev/server-openai-example.py`
- Added `DEV_MODE_IMPLEMENTATION.md`
- Added `USAGE_EXAMPLE.md`

### Technical Details

**Production Mode:**
```
Agent → LexiaHandler → CentrifugoClient → Centrifugo → WebSocket → Frontend
```

**Dev Mode:**
```
Agent → LexiaHandler → DevStreamClient → Memory → SSE/Poll → Frontend
                               ↓
                         Console Output
```

### Performance

- **Latency**: ~100ms poll interval (configurable)
- **Memory**: Minimal, streams auto-cleanup
- **Concurrent**: Thread-safe, unlimited streams
- **Timeout**: 5 minutes default (configurable)

### Examples

#### Backend
```python
from lexia import LexiaHandler, create_lexia_app, add_standard_endpoints

lexia = LexiaHandler(dev_mode=True)
app = create_lexia_app(title="My Agent")

async def process_message(data):
    for chunk in stream_response():
        lexia.stream_chunk(data, chunk)
    lexia.complete_response(data, full_response)

add_standard_endpoints(app, lexia_handler=lexia, process_message_func=process_message)
```

#### Frontend (JavaScript)
```javascript
const eventSource = new EventSource(`/api/v1/stream/${channel}`);

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === 'delta') {
        appendToChat(data.content);
    }
};
```

### Configuration Options

**Via Parameter:**
```python
lexia = LexiaHandler(dev_mode=True)
```

**Via Environment Variable:**
```bash
export LEXIA_DEV_MODE=true
```

**Via Command Line:**
```bash
python main.py --dev
```

### Testing

Run the example server:
```bash
cd lexia-frondend-python-dev
python server-openai-example.py
```

Expected output:
```
🔧 DEV MODE ACTIVE - No Centrifugo required!
📡 SSE Stream: http://localhost:5001/api/v1/stream/{channel}
```

### Next Steps

1. Try dev mode locally
2. Update your frontend to use SSE endpoint
3. Test without Centrifugo
4. Switch to production when ready

### Support

- Documentation: See `DEV_MODE_GUIDE.md`
- Examples: See `USAGE_EXAMPLE.md`
- Technical: See `DEV_MODE_IMPLEMENTATION.md`

---

**Upgrade Command:**
```bash
# If using local package
cd lexia-pip
python build_package.py

# If using pip (when published)
pip install --upgrade lexia
```

**Verify Dev Mode:**
```python
from lexia import LexiaHandler
lexia = LexiaHandler(dev_mode=True)
print(f"Dev mode: {lexia.dev_mode}")  # Should print: True
```

---

**Release Date:** October 10, 2025  
**Author:** Lexia Team  
**Version:** 1.2.2

