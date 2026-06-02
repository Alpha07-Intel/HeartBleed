import typer
from typing import Optional
from pathlib import Path
from .core.engine import SearchEngine
from .core.models import InputType
from .database.manager import DatabaseManager
from .reporters.terminal import TerminalReporter
from .reporters.html_gen import generate_html_report
from .exports.json_export import export_to_json
from .config import REPORTS_DIR, EXPORTS_DIR
from .utils.logger import logger

app = typer.Typer(help="HeartBleed: Advanced OSINT Identity Correlation Toolkit")
db = DatabaseManager()
reporter = TerminalReporter()

@app.callback()
def main_callback():
    """HeartBleed callback to print banner on every command."""
    reporter.print_banner()

@app.command()
def scan(
    value: str = typer.Argument(..., help="The identifier to search for (e.g., username, email, name)"),
    type: InputType = typer.Option(InputType.USERNAME, "--type", "-t", help="Type of input"),
    json: bool = typer.Option(False, "--json", help="Export results to JSON immediately"),
    html: bool = typer.Option(False, "--html", help="Generate HTML report immediately")
):
    """
    Scans multiple platforms for a given identifier and correlates results.
    """
    engine = SearchEngine()
    investigation = engine.run(type, value)
    
    # Save to DB
    inv_id = db.save_investigation(investigation)
    
    # Display results
    reporter.display_results(investigation)
    
    logger.info(f"\nInvestigation saved with ID: [bold]{inv_id}[/bold]")
    
    if json:
        path = EXPORTS_DIR / f"investigation_{inv_id}.json"
        export_to_json(investigation, path)
        logger.info(f"JSON export saved to: {path}")
        
    if html:
        path = REPORTS_DIR / f"report_{inv_id}.html"
        generate_html_report(investigation, path)
        logger.info(f"HTML report saved to: {path}")

@app.command()
def list(limit: int = typer.Option(10, help="Number of recent investigations to show")):
    """Lists recent investigations."""
    investigations = db.list_investigations(limit=limit)
    if not investigations:
        logger.info("No investigations found.")
        return
        
    from rich.table import Table
    table = Table(title="Recent Investigations")
    table.add_column("ID", style="cyan")
    table.add_column("Timestamp")
    table.add_column("Type")
    table.add_column("Value", style="green")
    
    for inv in investigations:
        table.add_row(str(inv["id"]), inv["timestamp"], inv["type"], inv["value"])
    
    from rich.console import Console
    Console().print(table)

@app.command()
def report(
    inv_id: int = typer.Argument(..., help="ID of the investigation"),
    format: str = typer.Option("terminal", "--format", "-f", help="Output format (terminal, html, json)")
):
    """Generates a report for a previous investigation."""
    investigation = db.get_investigation(inv_id)
    if not investigation:
        logger.error(f"Investigation with ID {inv_id} not found.")
        return
        
    if format == "terminal":
        reporter.display_results(investigation)
    elif format == "html":
        path = REPORTS_DIR / f"report_{inv_id}.html"
        generate_html_report(investigation, path)
        logger.info(f"HTML report generated at: {path}")
    elif format == "json":
        path = EXPORTS_DIR / f"investigation_{inv_id}.json"
        export_to_json(investigation, path)
        logger.info(f"JSON export saved to: {path}")

@app.command()
def clear(
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation")
):
    """Wipes the investigation history from the database."""
    if not force:
        confirm = typer.confirm("Are you sure you want to clear all investigation history?")
        if not confirm:
            logger.info("Operation cancelled.")
            return
            
    db.clear_all()
    logger.info("[bold green]All investigation history has been cleared.[/bold green]")

if __name__ == "__main__":
    app()
