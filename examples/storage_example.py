"""
Storage Example
===============

Demonstrates Orca Storage SDK usage.
"""

import sys
from pathlib import Path
import os

# Add parent directory to path for standalone execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from orca import OrcaStorage


def storage_example():
    """Example using high-level OrcaStorage client."""
    print("=" * 60)
    print("ORCA STORAGE SDK")
    print("=" * 60)
    print()
    
    # Initialize client
    storage = OrcaStorage(
        workspace=os.environ.get('ORCA_WORKSPACE', 'demo-workspace'),
        token=os.environ.get('ORCA_TOKEN', 'demo-token'),
        base_url=os.environ.get('STORAGE_URL', 'http://localhost:8000/api/v1/storage'),
        mode='dev'
    )
    
    print("✅ Client initialized")
    print()
    
    # Upload from buffer
    print("📤 Uploading from buffer...")
    try:
        content = b"Hello from Orca Storage!"
        file_info = storage.upload_buffer(
            bucket='demo-bucket',
            file_name='test.txt',
            buffer=content,
            folder_path='examples/',
            visibility='private',
            generate_url=True
        )
        print(f"   ✅ Uploaded: {file_info.get('key')}")
        print(f"   📍 URL: {file_info.get('download_url', 'N/A')[:50]}...")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    print()
    
    # List files
    print("📂 Listing files in 'demo-bucket'...")
    try:
        result = storage.list_files(
            bucket='demo-bucket',
            folder_path='examples/',
            page=1,
            per_page=10
        )
        files = result.get('files', [])
        print(f"   Found {len(files)} file(s)")
        for file in files:
            print(f"   - {file.get('key')} ({file.get('size')} bytes)")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    print()
    print("=" * 60)
    print()


def main():
    """Main example."""
    print()
    print("🗄️  Orca Storage SDK Demo")
    print()
    print("Note: Set these environment variables:")
    print("  - ORCA_WORKSPACE")
    print("  - ORCA_TOKEN")
    print("  - STORAGE_URL")
    print()
    
    # Run example
    storage_example()
    
    print("=" * 60)
    print("🔥 Storage SDK Demo Complete!")
    print("=" * 60)
    print()
    print("For complete documentation, see:")
    print("  - STORAGE_SDK_GUIDE.md")
    print()


if __name__ == "__main__":
    main()
