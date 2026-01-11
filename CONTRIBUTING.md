# Contributing to File Agent

Thank you for your interest in contributing to File Agent! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry
- Git

### Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Langgraph replicate with AI"
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Activate Poetry shell:**
   ```bash
   poetry shell
   ```

5. **Run tests to verify setup:**
   ```bash
   pytest
   ```

## Development Workflow

### Code Style

- **Formatting**: Use Black with line length 100
  ```bash
  poetry run black file_agent tests
  ```

- **Type Checking**: Use mypy
  ```bash
  poetry run mypy file_agent
  ```

- **Linting**: Use ruff
  ```bash
  poetry run ruff check file_agent tests
  ```

### Writing Tests

- Write tests for all new features
- Aim for high test coverage
- Use descriptive test names
- Group related tests in classes

Example:
```python
class TestNewFeature:
    def test_feature_success(self):
        """Test successful feature execution."""
        result = new_feature()
        assert result["success"] is True
```

### Commit Messages

Use clear, descriptive commit messages:
- Start with a verb (Add, Fix, Update, etc.)
- Be specific about what changed
- Reference issues if applicable

Examples:
- `Add support for batch file operations`
- `Fix path validation for Windows paths`
- `Update README with new examples`

## Project Structure

```
file-agent/
├── file_agent/      # Main package
├── tests/           # Test suite
├── docs/            # Documentation
└── ...
```

## Adding New Features

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement the feature:**
   - Write code following style guidelines
   - Add tests
   - Update documentation if needed

3. **Run tests and checks:**
   ```bash
   pytest
   poetry run black file_agent tests
   poetry run mypy file_agent
   poetry run ruff check file_agent tests
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

5. **Push and create a pull request**

## Adding New Tools

To add a new tool for the agent:

1. **Create the tool function in `agent.py`:**
   ```python
   @tool
   def your_tool(param: str) -> str:
       """Tool description for the agent."""
       # Implementation
       return result
   ```

2. **Add to tools list:**
   ```python
   tools = [
       # ... existing tools
       your_tool,
   ]
   ```

3. **Update system prompt if needed** in `prompts.py`

4. **Add tests** in `tests/test_agent.py`

## Adding New CLI Commands

1. **Add command function in `cli.py`:**
   ```python
   @app.command()
   def your_command(
       arg: str = typer.Argument(..., help="Description"),
   ) -> None:
       """Command description."""
       # Implementation
   ```

2. **Update README.md** with usage examples

3. **Add tests** in `tests/test_cli.py`

## Documentation

- Update README.md for user-facing changes
- Update architecture.md for architectural changes
- Add docstrings to all new functions and classes
- Use Google-style docstrings

## Questions?

If you have questions or need help, please open an issue on the repository.

Thank you for contributing!
