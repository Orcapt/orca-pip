#!/usr/bin/env python3
"""
Build Script for Orca Platform Package
========================================

This script builds the package and provides options for local installation and testing.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return None

def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed: {path}")
            elif path.is_file():
                path.unlink()
                print(f"   Removed: {path}")
    print("✅ Cleanup completed")

def build_package():
    """Build the package."""
    return run_command(
        "python3 -m build",
        "Building package"
    )

def install_locally():
    """Install the package locally for testing."""
    return run_command(
        "pip install -e .",
        "Installing package locally in editable mode"
    )

def test_import():
    """Test that the package can be imported."""
    print("🧪 Testing package import...")
    try:
        import orca
        from orca import OrcaHandler, ChatMessage, create_success_response
        print("✅ Package import successful")
        print(f"   Package version: {getattr(orca, '__version__', 'Not specified')}")
        return True
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

def show_usage():
    """Show usage information."""
    print("""
🚀 Orca Platform Package Builder
=================================

Usage:
  python build_package.py [command]

Commands:
  clean       - Clean build artifacts
  build       - Build the package
  install     - Install locally for testing
  test        - Test the package import
  all         - Clean, build, install, and test
  help        - Show this help message

Examples:
  python build_package.py build      # Just build the package
  python build_package.py install    # Install locally
  python build_package.py all        # Complete build process
""")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1].lower()
    
    if command == "clean":
        clean_build()
    elif command == "build":
        clean_build()
        build_package()
    elif command == "install":
        install_locally()
    elif command == "test":
        test_import()
    elif command == "all":
        clean_build()
        if build_package():
            if install_locally():
                test_import()
    elif command in ["help", "--help", "-h"]:
        show_usage()
    else:
        print(f"❌ Unknown command: {command}")
        show_usage()

if __name__ == "__main__":
    main()

