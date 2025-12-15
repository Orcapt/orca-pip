# Lexia Storage SDK

Simple storage client for Lexia platform.

## Quick Start

```python
from lexia import LexiaStorage

# Initialize
storage = LexiaStorage(
    workspace='my-workspace',
    token='my-token',
    base_url='https://api.example.com/api/v1/storage'
)

# Create bucket
bucket = storage.create_bucket('my-bucket')

# Upload file
file_info = storage.upload_file('my-bucket', 'report.pdf', folder='reports/2025/')

# Download file
storage.download_file('my-bucket', 'reports/2025/report.pdf', 'local.pdf')

# List files
files = storage.list_files('my-bucket', folder='reports/')
```

## Documentation

See [Lexia Storage SDK Developer Guide](../../../Lexia_storage%20_SDK_Developer_Guide.md) for complete documentation.
