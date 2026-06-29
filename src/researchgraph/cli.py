import typer
from rich.console import Console

from researchgraph.graph.runner import run_research

app = typer.Typer(help="ResearchGraph: Multi-Agent Deep Research CLI")
console = Console()

@app.command()
def version() -> None:
    """Print package version."""
    from researchgraph import __version__

    console.print(f"ResearchGraph {__version__}")

@app.command()
def research(query: str) -> None:
    """ Run a research task and export artifacts """
    final_state = run_research(query)
    console.print(f"Status: {final_state['status']}")
    console.print(f"Markdown: {final_state['exports']['markdown']}")
