from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from ..core.models import Investigation, CorrelationResult

class TerminalReporter:
    """Generates polished terminal output for investigations."""
    
    def __init__(self):
        self.console = Console()

    def print_banner(self):
        """Displays the HeartBleed ASCII banner and developer credits."""
        banner = r"""
[bold red]  _   _                      _   ____  _                 _ [/bold red]
[bold red] | | | | ___  __ _ _ __  _| |_| __ )| | ___  ___  __| |[/bold red]
[bold red] | |_| |/ _ \/ _` | '__| __|  _  |/ _ \/ _ \/ _` |[/bold red]
[bold red] |  _  |  __/ (_| | |  | |_| |_) | |  __/  __/ (_| |[/bold red]
[bold red] |_| |_|\___|\__,_|_|   \__|____/|_|\___|\___|\__,_|_|[/bold red]
                                                      
[bold white]        Advanced OSINT Identity Correlation Toolkit [bold green]v0.3[/bold green][/bold white]
[bold cyan]              Developed by: Alpha-07 (Metis Labs)[/bold cyan]
        """
        self.console.print(banner)

    def display_results(self, investigation: Investigation):
        """Prints a summary table and detailed correlation results."""
        self.console.print(f"\n[bold blue]Investigation Summary[/bold blue]")
        self.console.print(f"Target: {investigation.input_value} ({investigation.input_type.value})")
        self.console.print(f"Time: {investigation.timestamp}\n")

        if not investigation.correlations:
            self.console.print("[yellow]No profiles discovered.[/yellow]")
            return

        table = Table(title="Discovered Profiles & Correlation Score")
        table.add_column("Platform", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Score", justify="right")
        table.add_column("Confidence", style="magenta")

        for res in investigation.correlations:
            table.add_row(
                res.target_profile.platform,
                res.target_profile.username,
                str(res.score),
                res.confidence.value
            )

        self.console.print(table)
        
        # Details
        self.console.print("\n[bold]Correlation Details:[/bold]")
        for res in investigation.correlations:
            if res.match_reasons:
                reasons = ", ".join(res.match_reasons)
                self.console.print(f"* [cyan]{res.target_profile.platform}[/cyan]: {reasons}")

        # Persona Profile
        if investigation.persona_profile:
            self.console.print("\n[bold blue]Persona Profile (Local Analysis)[/bold blue]")
            for category, keywords in investigation.persona_profile.items():
                if keywords:
                    self.console.print(f"* [bold]{category}[/bold]: {', '.join(keywords)}")

        # Dorks
        if investigation.dorks:
            self.console.print("\n[bold yellow]Investigative Resources (Google Dorks)[/bold yellow]")
            for dork in investigation.dorks:
                self.console.print(f"* [bold]{dork['name']}[/bold]: {dork['url']}")
