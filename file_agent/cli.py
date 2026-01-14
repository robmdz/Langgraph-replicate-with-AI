"""CLI interface for the File Agent using Typer and Rich."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from file_agent.agent import run_agent
from file_agent.config import config
from file_agent.file_ops import list_directory, show_file

app = typer.Typer(
    name="file-agent",
    help="AI-powered CLI for creating, editing, and managing files through natural language",
    add_completion=False,
)
console = Console()


@app.command()
def create(
    prompt: str = typer.Argument(..., help="Natural language description of the file to create"),
    brief: bool = typer.Option(False, "--brief", help="Create ultra-concise summaries"),
    detailed: bool = typer.Option(False, "--detailed", help="Provide comprehensive breakdowns"),
    beginner: bool = typer.Option(False, "--beginner", help="Simplify for novice learners"),
    advanced: bool = typer.Option(False, "--advanced", help="Include sophisticated analysis"),
    questions: bool = typer.Option(False, "--questions", help="Focus on generating test questions"),
    flashcards: bool = typer.Option(False, "--flashcards", help="Format as Q&A pairs"),
    cornell: bool = typer.Option(False, "--cornell", help="Use Cornell note-taking format"),
    mindmap: bool = typer.Option(False, "--mindmap", help="Create text-based concept hierarchies"),
) -> None:
    """Create a new file using natural language description.

    This command uses the AI agent to create a new file based on a natural language
    description. The agent interprets the prompt and generates appropriate file content,
    which may include code, documentation, notes, or other text-based content.

    Args:
        prompt: Natural language description of the file to create. Examples:
            "a Python script that prints hello world"
            "a README file for a FastAPI project"
            "study notes on quantum physics"
        brief: If True, creates ultra-concise summaries. Useful for quick overviews.
        detailed: If True, provides comprehensive breakdowns with extensive detail.
        beginner: If True, simplifies content for novice learners.
        advanced: If True, includes sophisticated analysis and technical depth.
        questions: If True, focuses on generating test questions from content.
        flashcards: If True, formats output as Q&A pairs suitable for flashcards.
        cornell: If True, structures output in Cornell note-taking format.
        mindmap: If True, creates text-based hierarchical concept maps.

    Raises:
        typer.Exit: Exits with code 1 if configuration validation fails or if
            the agent encounters an error.

    Note:
        Multiple flags can be combined to customize the output format. The agent
        will adapt its behavior based on the active flags. A progress indicator
        is shown during file creation.
    """
    flags = {
        "brief": brief,
        "detailed": detailed,
        "beginner": beginner,
        "advanced": advanced,
        "questions": questions,
        "flashcards": flashcards,
        "cornell": cornell,
        "mindmap": mindmap,
    }

    try:
        config.validate()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating file...", total=None)
        response = run_agent(f"Create a file: {prompt}", flags)
        progress.update(task, completed=True)

    console.print("\n[green]✓[/green] File created successfully!")
    console.print(Panel(response, title="Agent Response", border_style="blue"))


@app.command()
def edit(
    file_path: str = typer.Argument(..., help="Path to the file to edit"),
    prompt: str = typer.Argument(..., help="Natural language description of the edit to make"),
    brief: bool = typer.Option(False, "--brief", help="Create ultra-concise summaries"),
    detailed: bool = typer.Option(False, "--detailed", help="Provide comprehensive breakdowns"),
    beginner: bool = typer.Option(False, "--beginner", help="Simplify for novice learners"),
    advanced: bool = typer.Option(False, "--advanced", help="Include sophisticated analysis"),
    questions: bool = typer.Option(False, "--questions", help="Focus on generating test questions"),
    flashcards: bool = typer.Option(False, "--flashcards", help="Format as Q&A pairs"),
    cornell: bool = typer.Option(False, "--cornell", help="Use Cornell note-taking format"),
    mindmap: bool = typer.Option(False, "--mindmap", help="Create text-based concept hierarchies"),
) -> None:
    """Edit an existing file using natural language description.

    This command uses the AI agent to modify an existing file based on a natural
    language description. The agent reads the current file content, interprets
    the edit request, and applies the changes appropriately.

    Args:
        file_path: Path to the file to edit (relative to current directory).
            The file must exist.
        prompt: Natural language description of the edit to make. Examples:
            "add error handling to the main function"
            "simplify the explanation for beginners"
            "add a summary section at the top"
        brief: If True, creates ultra-concise summaries. Useful for quick overviews.
        detailed: If True, provides comprehensive breakdowns with extensive detail.
        beginner: If True, simplifies content for novice learners.
        advanced: If True, includes sophisticated analysis and technical depth.
        questions: If True, focuses on generating test questions from content.
        flashcards: If True, formats output as Q&A pairs suitable for flashcards.
        cornell: If True, structures output in Cornell note-taking format.
        mindmap: If True, creates text-based hierarchical concept maps.

    Raises:
        typer.Exit: Exits with code 1 if configuration validation fails, if
            the file doesn't exist, or if the agent encounters an error.

    Note:
        The agent may read the file first to understand its current content before
        making edits. Multiple flags can be combined to customize the edit behavior.
        A progress indicator is shown during file editing.
    """
    flags = {
        "brief": brief,
        "detailed": detailed,
        "beginner": beginner,
        "advanced": advanced,
        "questions": questions,
        "flashcards": flashcards,
        "cornell": cornell,
        "mindmap": mindmap,
    }

    try:
        config.validate()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Editing file...", total=None)
        response = run_agent(f"Edit the file {file_path}: {prompt}", flags)
        progress.update(task, completed=True)

    console.print("\n[green]✓[/green] File edited successfully!")
    console.print(Panel(response, title="Agent Response", border_style="blue"))


@app.command()
def show(
    file_path: str = typer.Argument(..., help="Path to the file to display"),
) -> None:
    """Display file contents with syntax highlighting.

    This command displays the contents of a file with syntax highlighting based
    on the file extension. It also shows file metadata including path and size.

    Args:
        file_path: Path to the file to display (relative to current directory).
            The file must exist and not exceed the maximum file size limit.

    Raises:
        typer.Exit: Exits with code 1 if the file doesn't exist, if the file
            exceeds the maximum size limit, or if there's an error reading the file.

    Note:
        Syntax highlighting is automatically determined based on the file extension.
        Supported languages include Python, JavaScript, TypeScript, HTML, CSS,
        JSON, Markdown, YAML, TOML, Bash, Rust, Go, Java, C++, and C. Files
        exceeding MAX_FILE_SIZE will not be displayed for safety reasons.
    """
    result = show_file(file_path)

    if not result["success"]:
        console.print(f"[red]Error:[/red] {result['message']}")
        raise typer.Exit(1)

    # Display metadata
    metadata = result["metadata"]
    console.print(f"\n[dim]File:[/dim] {metadata['path']}")
    console.print(f"[dim]Size:[/dim] {metadata['size']}")

    # Display content with syntax highlighting
    content = result["content"]
    language = result["language"]

    syntax = Syntax(content, language, theme="monokai", line_numbers=True)
    console.print(syntax)


@app.command()
def chat(
    prompt: str = typer.Argument(..., help="Natural language prompt for the agent"),
    brief: bool = typer.Option(False, "--brief", help="Create ultra-concise summaries"),
    detailed: bool = typer.Option(False, "--detailed", help="Provide comprehensive breakdowns"),
    beginner: bool = typer.Option(False, "--beginner", help="Simplify for novice learners"),
    advanced: bool = typer.Option(False, "--advanced", help="Include sophisticated analysis"),
    questions: bool = typer.Option(False, "--questions", help="Focus on generating test questions"),
    flashcards: bool = typer.Option(False, "--flashcards", help="Format as Q&A pairs"),
    cornell: bool = typer.Option(False, "--cornell", help="Use Cornell note-taking format"),
    mindmap: bool = typer.Option(False, "--mindmap", help="Create text-based concept hierarchies"),
) -> None:
    """Chat with the agent for general file operations and learning assistance.

    This command provides a general-purpose interface to interact with the AI agent.
    It can handle various file operations, answer questions, create project structures,
    and provide learning assistance. The agent can perform multi-step operations and
    use tools as needed.

    Args:
        prompt: Natural language prompt for the agent. Examples:
            "create a project structure for a FastAPI app"
            "explain how to use decorators in Python"
            "generate practice questions for biology exam"
        brief: If True, creates ultra-concise summaries. Useful for quick overviews.
        detailed: If True, provides comprehensive breakdowns with extensive detail.
        beginner: If True, simplifies content for novice learners.
        advanced: If True, includes sophisticated analysis and technical depth.
        questions: If True, focuses on generating test questions from content.
        flashcards: If True, formats output as Q&A pairs suitable for flashcards.
        cornell: If True, structures output in Cornell note-taking format.
        mindmap: If True, creates text-based hierarchical concept maps.

    Raises:
        typer.Exit: Exits with code 1 if configuration validation fails or if
            the agent encounters an error.

    Note:
        This is the most flexible command, allowing the agent to decide which
        operations and tools to use based on the prompt. Multiple flags can be
        combined to customize the output format. A progress indicator is shown
        during processing.
    """
    flags = {
        "brief": brief,
        "detailed": detailed,
        "beginner": beginner,
        "advanced": advanced,
        "questions": questions,
        "flashcards": flashcards,
        "cornell": cornell,
        "mindmap": mindmap,
    }

    try:
        config.validate()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing...", total=None)
        response = run_agent(prompt, flags)
        progress.update(task, completed=True)

    console.print("\n")
    console.print(Panel(response, title="Agent Response", border_style="green"))


@app.command()
def list(
    directory: str | None = typer.Argument(None, help="Directory to list (default: current directory)"),
) -> None:
    """List directory contents.

    This command displays the contents of a directory in a formatted table,
    showing files with their sizes and directories with folder indicators.

    Args:
        directory: Path to the directory to list. If None, lists the current
            working directory. The path must exist and be a directory.

    Raises:
        typer.Exit: Exits with code 1 if the directory doesn't exist, if the
            path is not a directory, or if there's an error listing the directory.

    Note:
        Files are displayed with their human-readable sizes. Directories are
        marked with a folder icon. The listing is sorted alphabetically. Empty
        directories display a message indicating they are empty. Path validation
        prevents directory traversal attacks.
    """
    result = list_directory(directory)

    if not result["success"]:
        console.print(f"[red]Error:[/red] {result['message']}")
        raise typer.Exit(1)

    # Create table
    table = Table(title=f"Contents of {result['path']}")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Size", style="green", justify="right")

    items = result["items"]
    if not items:
        console.print(f"[yellow]Directory is empty:[/yellow] {result['path']}")
        return

    for item in items:
        if item["type"] == "file":
            table.add_row(item["name"], "📄 File", item["size"] or "N/A")
        else:
            table.add_row(item["name"], "📁 Directory", "-")

    console.print("\n")
    console.print(table)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
) -> None:
    """File Agent - AI-powered CLI for file operations.

    This is the main entry point for the File Agent CLI application. When invoked
    without a subcommand, it displays help information and example commands.

    Args:
        ctx: Typer context object containing invocation information.
        version: If True, displays the application version and exits.

    Raises:
        typer.Exit: Exits with code 0 after displaying version or help information.

    Note:
        This callback is invoked when no subcommand is provided. It shows a
        welcome message and example commands to help users get started.
    """
    if version:
        from file_agent import __version__

        console.print(f"file-agent version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print("[bold blue]File Agent[/bold blue] - AI-powered CLI for file operations")
        console.print("\nUse [cyan]file-agent --help[/cyan] to see available commands.")
        console.print("\nExample commands:")
        console.print("  [cyan]file-agent create \"a Python script that prints hello world\"[/cyan]")
        console.print("  [cyan]file-agent edit main.py \"add error handling\"[/cyan]")
        console.print("  [cyan]file-agent show config.json[/cyan]")
        console.print("  [cyan]file-agent chat \"create a project structure for FastAPI\"[/cyan]")


if __name__ == "__main__":
    app()
