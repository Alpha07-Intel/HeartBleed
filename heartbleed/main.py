import typer
from typing import Optional
from pathlib import Path
from .core.engine import SearchEngine
from .core.models import InputType
from .database.manager import DatabaseManager
from .reporters.terminal import TerminalReporter
from .reporters.html_gen import generate_html_report, generate_workspace_report
from .exports.json_export import export_to_json
from .exports.pdf_export import export_to_pdf
from .config import REPORTS_DIR, EXPORTS_DIR
from .utils.logger import logger

# App and Command Groups
app = typer.Typer(help="HeartBleed: Advanced OSINT Identity Correlation Toolkit")
workspace_app = typer.Typer(help="Manage multi-target investigation workspaces")
domain_app = typer.Typer(help="Domain intelligence and analysis modules")

app.add_typer(workspace_app, name="workspace")
app.add_typer(domain_app, name="domain")

db = DatabaseManager()
reporter = TerminalReporter()

@app.callback()
def main_callback():
    """HeartBleed callback to print banner on every command."""
    reporter.print_banner()

@app.command()
def scan(
    value: str = typer.Argument(..., help="The identifier to search for (username, email, or name)"),
    type: InputType = typer.Option(InputType.USERNAME, "--type", "-t", help="Type of input"),
    json: bool = typer.Option(False, "--json", help="Export results to JSON immediately"),
    html: bool = typer.Option(False, "--html", help="Generate HTML report immediately"),
    pdf: bool = typer.Option(False, "--pdf", help="Generate PDF report immediately"),
    workspace: Optional[int] = typer.Option(None, "--workspace", "-ws", help="Add this scan to a workspace ID"),
    mutate: bool = typer.Option(False, "--mutate", "-m", help="Automatically search for common username variations")
):
    """
    Scans multiple platforms for a given identifier and correlates results.
    """
    engine = SearchEngine()
    investigation = engine.run(type, value, mutate=mutate)
    
    # Save to DB
    inv_id = db.save_investigation(investigation)
    
    # Add to workspace if requested
    if workspace:
        db.add_to_workspace(workspace, inv_id)
        logger.info(f"Added to workspace [bold]{workspace}[/bold]")
    
    # Display results
    reporter.display_results(investigation)
    
    logger.info(f"\nInvestigation saved with ID: [bold]{inv_id}[/bold]")
    
    # Immediate Exports
    if json:
        path = EXPORTS_DIR / f"investigation_{inv_id}.json"
        export_to_json(investigation, path)
        logger.info(f"JSON export saved to: {path}")
        
    if html:
        path = REPORTS_DIR / f"report_{inv_id}.html"
        generate_html_report(investigation, path)
        logger.info(f"HTML report saved to: {path}")

    if pdf:
        path = REPORTS_DIR / f"report_{inv_id}.pdf"
        export_to_pdf(investigation, path)
        logger.info(f"PDF report saved to: {path}")

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
    format: str = typer.Option("terminal", "--format", "-f", help="Output format (terminal, html, json, pdf)")
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
    elif format == "pdf":
        path = REPORTS_DIR / f"report_{inv_id}.pdf"
        export_to_pdf(investigation, path)
        logger.info(f"PDF export saved to: {path}")

@app.command()
def clear(
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation")
):
    """Wipes all data from the database."""
    if not force:
        confirm = typer.confirm("Are you sure you want to clear all investigation history?")
        if not confirm:
            logger.info("Operation cancelled.")
            return
            
    db.clear_all()
    logger.info("[bold green]All investigation history and workspaces have been cleared.[/bold green]")

# Domain Commands
@domain_app.command("scan")
def domain_scan(domain: str = typer.Argument(..., help="Domain to analyze (e.g., example.com)")):
    """Analyzes a domain for WHOIS, DNS, and Subdomains."""
    from .modules.domain.whois_info import get_whois_data
    from .modules.domain.dns_info import get_dns_records
    from .modules.domain.subdomains import get_subdomains
    from rich.progress import Progress, SpinnerColumn, TextColumn

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description=f"Gathering intel for {domain}...", total=None)
        whois = get_whois_data(domain)
        dns = get_dns_records(domain)
        subs = get_subdomains(domain)

    from rich.panel import Panel
    from rich.console import Console
    console = Console()

    # 1. WHOIS Panel
    if whois:
        whois_text = "\n".join([f"[bold]{k}[/bold]: {v}" for k, v in whois.items()])
        console.print(Panel(whois_text, title=f"WHOIS Information: {domain}", border_style="cyan"))

    # 2. DNS Panel
    dns_text = ""
    for rtype, records in dns.items():
        if records:
            dns_text += f"[bold]{rtype} Records:[/bold]\n"
            dns_text += "\n".join([f"  * {r}" for r in records]) + "\n"
    if dns_text:
        console.print(Panel(dns_text, title="DNS Records", border_style="green"))

    # 3. Subdomains Panel
    if subs:
        sub_text = "\n".join([f"  * {s}" for s in subs[:20]])
        if len(subs) > 20: sub_text += f"\n  ... and {len(subs)-20} more"
        console.print(Panel(sub_text, title=f"Discovered Subdomains ({len(subs)})", border_style="magenta"))

# Workspace Commands
@workspace_app.command("create")
def workspace_create(
    name: str = typer.Argument(..., help="Name of the workspace"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Description")
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
    table.add_column("Created At")
    
    for ws in workspaces:
        table.add_row(str(ws["id"]), ws["name"], ws["created_at"])
    from rich.console import Console
    Console().print(table)

@workspace_app.command("report")
def workspace_report(ws_id: int = typer.Argument(..., help="Workspace ID")):
    """Generates a consolidated HTML map for a workspace."""
    workspace = db.get_workspace(ws_id)
    if not workspace:
        logger.error(f"Workspace {ws_id} not found.")
        return
    
    investigations = [db.get_investigation(i) for i in workspace.investigation_ids if db.get_investigation(i)]
    if not investigations:
        logger.warning("No investigations in this workspace.")
        return

    from .reporters.html_gen import generate_workspace_report
    path = REPORTS_DIR / f"workspace_report_{ws_id}.html"
    generate_workspace_report(workspace, investigations, path)
    logger.info(f"Workspace map generated at: {path}")

if __name__ == "__main__":
    app()
