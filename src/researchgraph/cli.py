import typer
from rich.console import Console

app = typer.Typer(help="ResearchGraph: Multi-Agent Deep Research CLI")
console = Console()


@app.callback()
def main() -> None:
    """ResearchGraph CLI."""
    pass


@app.command()
def version() -> None:
    """Print package version."""
    from researchgraph import __version__

    console.print(f"ResearchGraph {__version__}")
