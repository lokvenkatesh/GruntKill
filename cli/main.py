import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from dotenv import load_dotenv

load_dotenv()

app     = Console()
cli     = typer.Typer(help="GruntKill CLI — kill your repetitive dev work")

# ── helpers ──────────────────────────────────────────────

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ── commands ─────────────────────────────────────────────

@cli.command()
def status():
    """Show GruntKill status — patterns, scripts, risk reports"""
    app.print(Panel.fit("⚡ [bold green]GruntKill Status[/bold green]", border_style="green"))

    patterns = load_json("detected_patterns.json")
    reports  = load_json("risk_reports.json")

    # Count generated scripts
    scripts = [f for f in os.listdir(".") if f.startswith("generated_") and f.endswith(".py")]

    table = Table(box=box.SIMPLE)
    table.add_column("Component",   style="cyan",  no_wrap=True)
    table.add_column("Status",      style="green")
    table.add_column("Count",       style="white")

    table.add_row("Observer",         "✅ Ready",  "—")
    table.add_row("Patterns detected", "✅ Done",  str(len(patterns)))
    table.add_row("Scripts generated", "✅ Done",  str(len(scripts)))
    table.add_row("Risk reports",      "✅ Done",  str(len(reports)))

    app.print(table)

@cli.command()
def suggestions():
    """Show all pending automation suggestions"""
    patterns = load_json("detected_patterns.json")
    reports  = load_json("risk_reports.json")

    if not patterns:
        app.print("[yellow]⚠️  No suggestions yet. Run: python engine/pattern_detector.py[/yellow]")
        raise typer.Exit()

    app.print(Panel.fit("💡 [bold yellow]Pending Suggestions[/bold yellow]", border_style="yellow"))

    risk_map = {r["pattern_name"]: r for r in reports}

    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("#",            style="dim",    width=4)
    table.add_column("Pattern",      style="cyan",   no_wrap=True)
    table.add_column("Frequency",    style="white",  width=10)
    table.add_column("Risk",         style="white",  width=10)
    table.add_column("Auto-deploy",  style="white",  width=12)
    table.add_column("Description",  style="white")

    for i, p in enumerate(patterns, 1):
        name  = p.get("pattern_name", "unknown")
        freq  = str(p.get("frequency", "?")) + "×"
        desc  = p.get("description", "")[:60] + "..."
        risk  = risk_map.get(name, {})
        level = risk.get("risk_level", "unknown").lower()
        safe  = risk.get("safe_to_auto_deploy", False)

        emoji = {"low": "🟢 LOW", "medium": "🟡 MED", "high": "🔴 HIGH"}.get(level, "⚪ ?")
        auto  = "✅ Yes" if safe else "⚠️  No"

        table.add_row(str(i), name, freq, emoji, auto, desc)

    app.print(table)
    app.print("\n[dim]Run [cyan]gk approve <number>[/cyan] to approve a suggestion[/dim]")

@cli.command()
def approve(number: int = typer.Argument(..., help="Suggestion number to approve")):
    """Approve a suggestion and trigger deployment"""
    patterns = load_json("detected_patterns.json")
    reports  = load_json("risk_reports.json")

    if not patterns:
        app.print("[yellow]⚠️  No suggestions found.[/yellow]")
        raise typer.Exit()

    if number < 1 or number > len(patterns):
        app.print(f"[red]❌ Invalid number. Choose between 1 and {len(patterns)}[/red]")
        raise typer.Exit()

    pattern = patterns[number - 1]
    name    = pattern.get("pattern_name", "unknown")
    risk_map = {r["pattern_name"]: r for r in reports}
    risk    = risk_map.get(name, {})
    level   = risk.get("risk_level", "unknown")

    app.print(Panel.fit(f"[bold]Approving: [cyan]{name}[/cyan][/bold]", border_style="cyan"))

    # Warn if risky
    if level == "high":
        app.print(f"[red]⚠️  WARNING: This script is rated HIGH RISK[/red]")
        confirm = typer.confirm("Are you sure you want to deploy?")
        if not confirm:
            app.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit()

    # Send Slack deployed notification
    try:
        from notifications.slack import send_deployed
        send_deployed(name)
        app.print("✅ [green]Slack notified — deployment triggered[/green]")
    except Exception as e:
        app.print(f"[yellow]⚠️  Slack notification failed: {e}[/yellow]")

    # Save approval record
    approvals = load_json("approvals.json")
    approvals.append({
        "pattern_name": name,
        "approved_at":  __import__("datetime").datetime.now().isoformat(),
        "risk_level":   level
    })
    save_json("approvals.json", approvals)

    app.print(f"\n🚀 [bold green]{name}[/bold green] approved and queued for deployment!")
    app.print("[dim]AWS Lambda deployment will be wired up in Week 4[/dim]")

@cli.command()
def reject(number: int = typer.Argument(..., help="Suggestion number to reject")):
    """Reject a suggestion"""
    patterns = load_json("detected_patterns.json")

    if not patterns:
        app.print("[yellow]⚠️  No suggestions found.[/yellow]")
        raise typer.Exit()

    if number < 1 or number > len(patterns):
        app.print(f"[red]❌ Invalid number. Choose between 1 and {len(patterns)}[/red]")
        raise typer.Exit()

    pattern = patterns[number - 1]
    name    = pattern.get("pattern_name", "unknown")

    try:
        from notifications.slack import send_rejected
        send_rejected(name)
    except Exception as e:
        app.print(f"[yellow]⚠️  Slack notification failed: {e}[/yellow]")

    app.print(f"❌ [red]{name}[/red] rejected.")

@cli.command()
def logs(limit: int = typer.Option(20, help="Number of recent logs to show")):
    """Show recent activity logs from the database"""
    from observer.activity_logger import get_recent_activity

    rows = get_recent_activity(days=7)
    shell_rows = [r for r in rows if r[1] == "shell_command"][-limit:]

    if not shell_rows:
        app.print("[yellow]⚠️  No logs yet. Run: python observer/shell_hook.py[/yellow]")
        raise typer.Exit()

    app.print(Panel.fit(f"📋 [bold]Recent Activity[/bold] (last {len(shell_rows)} commands)", border_style="blue"))

    table = Table(box=box.SIMPLE)
    table.add_column("Time",     style="dim",  no_wrap=True, width=22)
    table.add_column("Command",  style="cyan")
    table.add_column("Dir",      style="dim")

    for row in shell_rows:
        timestamp, event_type, data, cwd = row
        short_cwd = (cwd or "").replace(os.path.expanduser("~"), "~")[-30:]
        table.add_row(timestamp[:19], data[:60], short_cwd)

    app.print(table)

@cli.command()
def scan():
    """Run full GruntKill scan — detect patterns + score risk + notify Slack"""
    app.print(Panel.fit("🔍 [bold]Running Full GruntKill Scan[/bold]", border_style="green"))

    # Step 1 — detect patterns
    app.print("\n[cyan]Step 1/3 — Detecting patterns...[/cyan]")
    from engine.pattern_detector import detect_patterns, print_patterns
    patterns = detect_patterns(days=7)
    print_patterns(patterns)

    if not patterns:
        app.print("[yellow]No patterns found yet. Log more commands first.[/yellow]")
        raise typer.Exit()

    # Step 2 — score risk
    app.print("\n[cyan]Step 2/3 — Scoring risk...[/cyan]")
    from risk.scorer import score_generated_scripts
    reports = score_generated_scripts()

    # Step 3 — notify Slack
    app.print("\n[cyan]Step 3/3 — Sending Slack notifications...[/cyan]")
    from notifications.slack import send_suggestion
    risk_map = {r["pattern_name"]: r for r in reports}
    for p in patterns:
        risk = risk_map.get(p.get("pattern_name", ""), {})
        send_suggestion(p, risk)

    app.print("\n✅ [bold green]Scan complete![/bold green]")
    app.print("[dim]Check your Slack channel for suggestions[/dim]")

if __name__ == "__main__":
    cli()