# File Agent - AI-Powered CLI for File Operations

A command-line interface (CLI) application that uses an AI agent to create, edit, and display files through natural language commands. Built with Python, LangChain/LangGraph, Typer, and Rich.

## Features

- **Natural Language File Operations**: Create, edit, and manage files using plain English
- **Learning Notes Assistant**: Specialized AI agent for processing and organizing study materials
- **Beautiful CLI**: Rich terminal output with syntax highlighting, tables, and progress indicators
- **Safe & Secure**: Path validation, confirmation prompts, and file size limits
- **Multi-format Support**: Generate content in various formats (Cornell notes, flashcards, mind maps, etc.)

## Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- OpenAI API key

### Step-by-Step Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd "Langgraph replicate with AI"
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```
   
   Or set it in your environment:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

5. **Install the package** (for development):
   ```bash
   poetry run pip install -e .
   ```

   Or activate the Poetry shell:
   ```bash
   poetry shell
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o
MAX_FILE_SIZE=10485760  # Optional, defaults to 10MB
```

### Getting an OpenAI API Key

1. Visit [OpenAI's website](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to the API keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Usage

### Basic Commands

**Create a file:**
```bash
file-agent create "a Python script that prints hello world"
```

**Edit an existing file:**
```bash
file-agent edit main.py "add error handling to the main function"
```

**Display file contents:**
```bash
file-agent show config.json
```

**Chat with the agent:**
```bash
file-agent chat "create a project structure for a FastAPI app"
```

**List directory contents:**
```bash
file-agent list
file-agent list /path/to/directory
```

### Special Flags

The agent supports various flags to customize output format:

- `--brief`: Create ultra-concise summaries
- `--detailed`: Provide comprehensive breakdowns
- `--beginner`: Simplify for novice learners
- `--advanced`: Include sophisticated analysis
- `--questions`: Focus on generating test questions
- `--flashcards`: Format as Q&A pairs
- `--cornell`: Use Cornell note-taking format
- `--mindmap`: Create text-based concept hierarchies

**Examples:**
```bash
file-agent create "summarize these lecture notes" --brief
file-agent chat "explain quantum physics" --beginner
file-agent create "study guide for biology exam" --flashcards
```

### Example Workflows

**Creating Study Materials:**
```bash
# Create a summary from lecture notes
file-agent create "summarize the key concepts from my biology notes" --cornell

# Generate practice questions
file-agent chat "create practice questions from chapter 5" --questions

# Create flashcards
file-agent create "flashcards for vocabulary terms" --flashcards
```

**File Management:**
```bash
# Create a new Python project
file-agent chat "create a FastAPI project with authentication"

# Refactor code
file-agent edit app.py "add type hints and docstrings to all functions"

# Review file contents
file-agent show requirements.txt
```

## Project Structure

```
file-agent/
├── file_agent/
│   ├── __init__.py
│   ├── agent.py          # LangGraph agent with tools
│   ├── cli.py            # Typer CLI interface
│   ├── file_ops.py       # File operation utilities
│   ├── config.py        # Configuration management
│   ├── prompts.py        # System prompts
│   └── utils.py          # Helper functions
├── tests/
│   ├── test_agent.py
│   ├── test_cli.py
│   └── test_file_ops.py
├── docs/
│   └── architecture.md
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
└── LICENSE
```

## Development

### Running Tests

```bash
poetry run pytest
```

With coverage:
```bash
poetry run pytest --cov=file_agent --cov-report=html
```

### Code Quality

Format code:
```bash
poetry run black file_agent tests
```

Type checking:
```bash
poetry run mypy file_agent
```

Linting:
```bash
poetry run ruff check file_agent tests
```

## Troubleshooting

### "OPENAI_API_KEY is not set" Error

**Solution**: Make sure you've created a `.env` file with your API key, or set the environment variable:
```bash
export OPENAI_API_KEY=your_key_here
```

### "Path is outside the allowed directory" Error

**Solution**: The agent prevents directory traversal attacks. Make sure you're using relative paths within your current working directory.

### File Size Exceeded Error

**Solution**: The default maximum file size is 10MB. You can increase it by setting `MAX_FILE_SIZE` in your `.env` file (value in bytes).

### Import Errors

**Solution**: Make sure you've installed all dependencies:
```bash
poetry install
```

If using the package directly:
```bash
pip install -e .
```

## Security Considerations

- **API Keys**: Never commit your `.env` file or expose API keys in code
- **Path Validation**: All file paths are validated to prevent directory traversal attacks
- **File Size Limits**: Maximum file size is enforced to prevent abuse
- **Confirmation Prompts**: Destructive operations require explicit confirmation

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for development setup instructions.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- CLI powered by [Typer](https://typer.tiangolo.com/)
- Beautiful output with [Rich](https://rich.readthedocs.io/)
