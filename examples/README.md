# Lexia SDK Examples

Comprehensive examples demonstrating Lexia SDK features.

## Examples

### 1. `basic_usage.py`

Basic streaming and button usage.

```bash
python examples/basic_usage.py
```

### 2. `advanced_usage.py`

Advanced features: decorators, logging, usage tracking.

```bash
python examples/advanced_usage.py
```

### 3. `error_handling.py`

Comprehensive error handling patterns.

```bash
python examples/error_handling.py
```

## Key Concepts

### Streaming

```python
session = handler.begin(data)
session.stream("Hello, world!")
```

### Loading Indicators

```python
from lexia.config import LoadingKind
session.start_loading(LoadingKind.THINKING.value)
session.stream("Processing...")
session.end_loading(LoadingKind.THINKING.value)
```

### Buttons

```python
from lexia.config import ButtonColor
session.button.link("Click", "https://example.com", color=ButtonColor.PRIMARY.value)
```

### Error Handling

```python
from lexia.exceptions import LexiaException
try:
    # operations
except LexiaException as e:
    logger.error(f"Error: {e.to_dict()}")
```

### Decorators

```python
from lexia.decorators import retry, log_execution

@retry(max_attempts=3)
@log_execution
def process_data():
    pass
```

### Logging

```python
from lexia.logging_config import setup_logging
setup_logging(level=logging.DEBUG, log_file="app.log")
```
