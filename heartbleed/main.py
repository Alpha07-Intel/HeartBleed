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
workspace_app = typer.Typer(help="Manage multi-target investigation workspaces")
app.add_typer(workspace_app, name="workspace")

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
    html: bool = typer.Option(False, "--html", help="Generate HTML report immediately"),
    workspace: Optional[int] = typer.Option(None, "--workspace", "-ws", help="Add this scan to a specific workspace ID")
):
    """
    Scans multiple platforms for a given identifier and correlates results.
    """
    engine = SearchEngine()
    investigation = engine.run(type, value)
    
    # Save to DB
    inv_id = db.save_investigation(investigation)
    
    # Add to workspace if requested
    if workspace:
        db.add_to_workspace(workspace, inv_id)
        logger.info(f"Added to workspace [bold]{workspace}[/bold]")
    
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
    logger.info("[bold green]All investigation history and workspaces have been cleared.[/bold green]")

# Workspace Commands
@workspace_app.command("create")
def workspace_create(
    name: str = typer.Argument(..., help="Name of the workspace"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Description of the workspace")
):
    """Creates a new workspace."""
    ws_id = db.create_workspace(name, description)
    logger.info(f"Workspace [bold]{name}[/bold] created with ID: [bold]{ws_id}[/bold]")

@workspace_app.command("list")
def workspace_list():
    """Lists all workspaces."""
    workspaces = db.list_workspaces()
    if not workspaces:
        logger.info("No workspaces found.")
        return
        
    from rich.table import Table
    table = Table(title="Investigation Workspaces")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Created At")
    
    for ws in workspaces:
        table.add_row(str(ws["id"]), ws["name"], ws["description"] or "", ws["created_at"])
    
    from rich.console import Console
    Console().print(table)

@workspace_app.command("add")
def workspace_add(
    ws_id: int = typer.Argument(..., help="Workspace ID"),
    inv_id: int = typer.Argument(..., help="Investigation ID")
):
    """Adds an investigation to a workspace."""
    db.add_to_workspace(ws_id, inv_id)
    logger.info(f"Investigation {inv_id} added to workspace {ws_id}")

@workspace_app.command("report")
def workspace_report(
    ws_id: int = typer.Argument(..., help="Workspace ID"),
    format: str = typer.Option("html", "--format", "-f", help="Output format (currently only html supported for workspaces)")
):
    """Generates a consolidated report for all targets in a workspace."""
    workspace = db.get_workspace(ws_id)
    if not workspace:
        logger.error(f"Workspace {ws_id} not found.")
        return
    
    investigations = []
    for inv_id in workspace.investigation_ids:
        inv = db.get_investigation(inv_id)
        if inv:
            investigations.append(inv)
            
    if not investigations:
        logger.warning("No investigations found in this workspace.")
        return

    if format == "html":
        # We need a new reporter method for workspace reports
        from .reporters.html_gen import generate_workspace_report
        path = REPORTS_DIR / f"workspace_report_{ws_id}.html"
        generate_workspace_report(workspace, investigations, path)
        logger.info(f"Consolidated HTML report generated at: {path}")

if __name__ == "__main__":
    app()
