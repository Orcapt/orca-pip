# Changelog

All notable changes to the Lexia Platform Integration Package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.13] - 2025-11-17

### Added
- Added `usage()` method to SessionContext for tracking LLM token usage and costs
  - Supports prompt, completion, function_call, tool_usage token tracking
  - Optional cost tracking with string format
  - Optional custom labels for usage entries
  - Automatically uses message UUID from session data
  - Sends usage data to Lexia API `/api/internal/v1/usages` endpoint
  - Non-blocking - doesn't fail the request if usage tracking fails

### Changed
- Enhanced `response_handler.py` to handle both dictionary and OpenAI `CompletionUsage` objects for usage_info
- Updated package metadata and documentation for clarity
- Fixed version consistency across README, Makefile, and package files
- Updated license format in `pyproject.toml` to modern SPDX format (removed deprecated table format)
- Removed deprecated "License :: OSI Approved :: MIT License" classifier from both `setup.py` and `pyproject.toml`
- Code cleanup: removed extra blank lines in `utils.py`

### Fixed
- Updated test examples to use correct API (removed non-existent convenience methods)
- Fixed version references in documentation examples

## [1.2.12] - 2025-11-16

### Fixed
- Package fixes and improvements

## [1.2.11] - 2025-11-15

### Changed
- Version bump for package release

## [1.2.8] - 2025-11-02

### Added
- Added `sleep_time` parameter to `ChatMessage` model for configurable timing control
- Added `force_tools` parameter to `ChatMessage` model (list of tool names like ['code', 'search', 'xyz'])
- Added `ForceToolsHelper` class for easy access to forced tools with flexible `has()` method

### Removed
- Removed deprecated `force_search` boolean parameter (replaced by `force_tools`)
- Removed deprecated `force_code` boolean parameter (replaced by `force_tools`)

### Changed
- Tool forcing now uses a flexible list-based approach instead of individual boolean flags

## [1.2.6] - 2025-01-14

### Added
- Error logging to Lexia backend via `/api/internal/v1/logs` endpoint
- Enhanced `send_error()` method with optional `trace` and `exception` parameters for detailed error logging
- Automatic extraction and truncation of stack traces for error logs
- Support for error level, location tracking, and additional metadata in error logs

### Fixed
- Fixed Centrifugo client to send actual error message instead of hardcoded text
- Fixed dev mode error streaming to match normal response flow (delta + complete)
- Improved error message visibility in both dev and production modes

## [1.1.0] - 2025-08-18

### Added
- Initial release of Lexia Platform Integration Package
- `LexiaHandler` class for unified communication interface
- Data models for Lexia platform compatibility
- Response handling utilities
- FastAPI integration with standard endpoints
- Real-time streaming support
- Environment variable management
- API key handling utilities

### Features
- Clean, minimal package design
- Platform-agnostic AI agent integration
- Comprehensive error handling
- Easy-to-use API for developers
- Professional package structure
- MIT license for open source use

### Documentation
- Comprehensive README with examples
- Installation and usage instructions
- Development setup guide
- Contributing guidelines
- GitHub Actions CI workflow


