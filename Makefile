.PHONY: help clean build install test publish clean-all

# Default target
help:
	@echo "🚀 Orca Platform Package - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "📦 Package Management:"
	@echo "  make build          - Build the package"
	@echo "  make install        - Install locally for development"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make clean-all      - Clean everything including virtual env"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test           - Test package import"
	@echo "  make test-full      - Run full test suite"
	@echo ""
	@echo "🚀 Publishing:"
	@echo "  make publish        - Build and publish to PyPI (requires credentials)"
	@echo "  make publish-test   - Build and publish to Test PyPI"
	@echo ""
	@echo "📋 Development:"
	@echo "  make venv           - Create virtual environment"
	@echo "  make deps           - Install dependencies"
	@echo "  make format         - Format code with black"
	@echo "  make lint           - Run linting checks"
	@echo ""

# Create virtual environment
venv:
	@echo "🐍 Creating virtual environment..."
	python3 -m venv orca_env
	@echo "✅ Virtual environment created. Activate with: source orca_env/bin/activate"

# Install dependencies
deps:
	@echo "📦 Installing dependencies..."
	pip install -r orca/requirements.txt
	pip install build twine pytest black flake8

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "✅ Cleanup completed"

# Clean everything including virtual environment
clean-all: clean
	@echo "🧹 Cleaning virtual environment..."
	rm -rf orca_env/
	@echo "✅ Full cleanup completed"

# Build the package
build: clean
	@echo "🔨 Building package..."
	@if [ -d "build_env" ]; then \
		build_env/bin/python -m build; \
	else \
		python3 -m venv build_env && build_env/bin/pip install build wheel && build_env/bin/python -m build; \
	fi
	@echo "✅ Package built successfully"

# Install locally for development
install: build
	@echo "📥 Installing package locally..."
	pip install -e .
	@echo "✅ Package installed locally"

# Test package import
test:
	@echo "🧪 Testing package import..."
	python3 -c "import orca; from orca import OrcaHandler; print('✅ Import successful')"

# Run full test suite
test-full:
	@echo "🧪 Running full test suite..."
	python3 -m pytest tests/ -v

# Format code
format:
	@echo "🎨 Formatting code..."
	black orca/ --line-length 88
	@echo "✅ Code formatting completed"

# Run linting
lint:
	@echo "🔍 Running linting checks..."
	flake8 orca/ --max-line-length 88 --ignore E203,W503
	@echo "✅ Linting completed"

# Build and publish to PyPI
publish: build
	@echo "🚀 Publishing to PyPI..."
	twine upload dist/*
	@echo "✅ Package published to PyPI"

# Build and publish to Test PyPI
publish-test: build
	@echo "🧪 Publishing to Test PyPI..."
	twine upload --repository testpypi dist/*
	@echo "✅ Package published to Test PyPI"

# Quick development setup
dev: venv
	@echo "🔧 Setting up development environment..."
	@echo "Please activate the virtual environment:"
	@echo "  source orca_env/bin/activate"
	@echo "Then run: make deps"

# Show package info
info:
	@echo "📋 Package Information:"
	@echo "  Name: orcapt-sdk (PyPI)"
	@echo "  Module: orca (Python import)"
	@echo "  Version: 1.0.0"
	@echo "  Description: Clean, minimal package for Orca platform integration"
	@echo "  Python: >=3.8"
	@echo "  Dependencies: requests, pydantic"
	@echo "  Optional: fastapi, uvicorn (web), pytest, black, flake8 (dev)"
	@echo ""
	@echo "  Install: pip install orcapt-sdk"
	@echo "  Import:  from orca import OrcaHandler"

