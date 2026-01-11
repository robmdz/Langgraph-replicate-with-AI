# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-XX

### Added

- Initial release of File Agent
- CLI interface with Typer
- LangGraph agent with file operation tools
- Learning Notes Assistant system prompt
- File operations: create, edit, show, delete, list
- Rich terminal output with syntax highlighting
- Configuration management with environment variables
- Path validation and security features
- File size limits
- Special flags: --brief, --detailed, --beginner, --advanced, --questions, --flashcards, --cornell, --mindmap
- Comprehensive test suite
- Documentation: README, architecture docs, contributing guide

### Security

- Path validation to prevent directory traversal attacks
- File size limits to prevent abuse
- Secure API key management

[0.1.0]: https://github.com/yourusername/file-agent/releases/tag/v0.1.0
