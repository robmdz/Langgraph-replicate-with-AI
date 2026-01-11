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
    """Create a new file using natural language description."""
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
    """Edit an existing file using natural language description."""
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
    """Display file contents with syntax highlighting."""
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
    """Chat with the agent for general file operations and learning assistance."""
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
    """List directory contents."""
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
    """File Agent - AI-powered CLI for file operations."""
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
