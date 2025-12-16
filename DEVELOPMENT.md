# Development Guide

Quick guide for testing Lexia package locally during development.

## Local Installation for Testing

### Option 1: Editable Install (Recommended)

Install the package in editable/development mode:

```bash
# Navigate to package directory
cd /home/younes/Desktop/Company/Defraged/seitech/GptClone/lexia-repo/lexia-pip

# Install in editable mode
pip install -e .
```

**Benefits:**

- Changes to code are immediately reflected
- No need to reinstall after each change
- Perfect for development and testing

### Option 2: Regular Install

```bash
pip install .
```

**Note:** You'll need to reinstall after each change.

### Option 3: Install with Development Dependencies

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or install all extras
pip install -e ".[dev,web]"
```

## Quick Test

After installation, test if everything works:

```python
# test_local.py
from lexia import LexiaHandler, ChatMessage, LexiaStorage

# Test 1: Basic Handler
print("Testing LexiaHandler...")
handler = LexiaHandler(dev_mode=True)
print("✅ LexiaHandler works!")

# Test 2: ChatMessage
print("\nTesting ChatMessage...")
data = ChatMessage(
    message="Test",
    response_uuid="test-123",
    thread_id="thread-1",
    model="gpt-4",
    conversation_id=1,
    message_uuid="msg-1",
    channel="test",
    variables=[],
    stream_url="http://test.com",
    stream_token="token",
    url="http://test.com"
)
print("✅ ChatMessage works!")

# Test 3: Session
print("\nTesting Session...")
session = handler.begin(data)
session.stream("Hello World!")
response = session.close()
print(f"✅ Session works! Response: {response}")

# Test 4: Storage SDK
print("\nTesting Storage SDK...")
storage = LexiaStorage(
    workspace="test",
    token="test-token",
    base_url="https://test.com"
)
print("✅ Storage SDK works!")

print("\n🎉 All tests passed!")
```

Run the test:

```bash
python test_local.py
```

## Testing Changes

### 1. Make Changes

Edit any file in `lexia/`:

```python
# lexia/core/handler.py
# Make your changes...
```

### 2. Test Immediately (with editable install)

```python
# test_changes.py
from lexia import LexiaHandler

handler = LexiaHandler(dev_mode=True)
# Your changes are immediately available!
```

### 3. Run Official Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_package.py
```

## Common Development Tasks

### Check Package is Installed

```bash
pip list | grep lexia
```

Expected output:

```
lexia    2.0.0    /path/to/lexia-pip
```

### Uninstall Package

```bash
pip uninstall lexia
```

### Reinstall After Major Changes

```bash
pip uninstall lexia
pip install -e .
```

### Check Import Paths

```python
import lexia
print(lexia.__file__)
# Should show your local path
```

## Testing Specific Features

### Test Storage SDK

```python
from lexia import LexiaStorage

storage = LexiaStorage(
    workspace="my-workspace",
    token="my-token",
    base_url="http://localhost:8000/api/v1/storage"
)

# Test bucket operations
try:
    buckets = storage.list_buckets()
    print(f"Buckets: {buckets}")
except Exception as e:
    print(f"Note: {e} (expected if server not running)")
```

### Test Lambda Adapter

```python
from lexia import LambdaAdapter, ChatMessage

adapter = LambdaAdapter()

@adapter.message_handler
async def test_handler(data: ChatMessage):
    print("Handler called!")
    return "OK"

print("✅ Lambda adapter works!")
```

### Test Patterns

```python
from lexia.patterns import LexiaBuilder, MiddlewareChain

# Test Builder
handler = (LexiaBuilder()
    .with_dev_mode(True)
    .build())
print("✅ Builder works!")

# Test Middleware
chain = MiddlewareChain()
print("✅ Middleware works!")
```

## Debugging Tips

### Enable Debug Logging

```python
from lexia.common import setup_logging, enable_debug_logging
import logging

# Method 1: Setup with debug level
setup_logging(level=logging.DEBUG)

# Method 2: Enable debug for all loggers
enable_debug_logging()
```

### Check Module Imports

```python
import sys
import lexia

print("Lexia location:", lexia.__file__)
print("Lexia version:", lexia.__version__)
print("\nAvailable exports:")
print(lexia.__all__)
```

### Verify SOLID Refactoring

```python
# Test new storage architecture
from lexia.storage import (
    BaseStorageClient,
    BucketService,
    FileService,
    PermissionService,
    LexiaStorage
)

# All should import successfully
print("✅ All storage services available!")
```

## Virtual Environment (Recommended)

### Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install package
pip install -e .
```

### Deactivate

```bash
deactivate
```

## Example Test Script

Create `test_all_features.py`:

```python
#!/usr/bin/env python3
"""
Comprehensive local test for Lexia SDK
"""

from lexia import (
    LexiaHandler,
    ChatMessage,
    LexiaStorage,
    LambdaAdapter,
    LexiaBuilder,
)
from lexia.patterns import MiddlewareChain
from lexia.common import setup_logging

def test_core():
    """Test core functionality"""
    print("Testing Core...")
    handler = LexiaHandler(dev_mode=True)

    data = ChatMessage(
        message="Test",
        response_uuid="test-123",
        thread_id="thread-1",
        model="gpt-4",
        conversation_id=1,
        message_uuid="msg-1",
        channel="test",
        variables=[],
        stream_url="http://test.com",
        stream_token="token",
        url="http://test.com"
    )

    session = handler.begin(data)
    session.stream("Test message")
    response = session.close()

    print(f"  ✅ Core works! Response length: {len(response)}")

def test_storage():
    """Test storage SDK"""
    print("Testing Storage SDK...")
    storage = LexiaStorage(
        workspace="test",
        token="test-token",
        base_url="https://test.com"
    )
    print("  ✅ Storage SDK instantiated!")

def test_lambda():
    """Test lambda adapter"""
    print("Testing Lambda Adapter...")
    adapter = LambdaAdapter()
    print("  ✅ Lambda adapter works!")

def test_patterns():
    """Test patterns"""
    print("Testing Patterns...")
    handler = LexiaBuilder().with_dev_mode(True).build()
    chain = MiddlewareChain()
    print("  ✅ Patterns work!")

if __name__ == "__main__":
    print("="*60)
    print("LEXIA SDK - LOCAL TEST")
    print("="*60)
    print()

    test_core()
    test_storage()
    test_lambda()
    test_patterns()

    print()
    print("="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
```

Run it:

```bash
chmod +x test_all_features.py
python test_all_features.py
```

## Troubleshooting

### ImportError: No module named 'lexia'

**Solution:**

```bash
# Make sure you're in the right directory
cd /path/to/lexia-pip

# Install package
pip install -e .
```

### Changes not reflected

**Solution:**

```bash
# For editable install, just restart Python
# Or reimport the module
import importlib
import lexia
importlib.reload(lexia)
```

### Module not found in subdirectories

**Solution:**
Check `__init__.py` files exist in all directories.

## Production Testing

Before deploying to production:

```bash
# 1. Run all tests
python -m pytest tests/ -v

# 2. Check imports work
python -c "from lexia import *; print('OK')"

# 3. Verify version
python -c "import lexia; print(lexia.__version__)"

# 4. Build distribution
python setup.py sdist bdist_wheel

# 5. Test installation from wheel
pip install dist/lexia-2.0.0-py3-none-any.whl
```

## Quick Commands Reference

```bash
# Install for development
pip install -e .

# Install with extras
pip install -e ".[dev,web]"

# Run tests
python -m pytest tests/

# Check package
pip show lexia

# Uninstall
pip uninstall lexia

# Build package
python setup.py sdist bdist_wheel

# Clean build files
rm -rf build/ dist/ *.egg-info
```

## Next Steps

After local testing is successful:

1. **Commit changes**: `git add . && git commit -m "Your message"`
2. **Push to repo**: `git push origin main`
3. **Create release**: Tag with version number
4. **Deploy to PyPI**: `twine upload dist/*`

---

Happy development! 🚀
