"""CLI commands for audit log inspection in envault."""

import json
import click
from envault.audit import get_log, clear_log


@click.group("audit")
def audit_group():
    """Manage the vault audit log."""


@audit_group.command("log")
@click.option("--format", "fmt", default="table", type=click.Choice(["table", "json"]),
              show_default=True, help="Output format.")
@click.option("--vault-dir", default=".", hidden=True)
def cmd_audit_log(fmt, vault_dir):
    """Display the audit log for the current vault."""
    entries = get_log(vault_dir)
    if not entries:
        click.echo("No audit log entries found.")
        return

    if fmt == "json":
        click.echo(json.dumps(entries, indent=2))
    else:
        header = f"{'TIMESTAMP':<32} {'ACTOR':<16} {'ACTION':<12} {'KEY'}"
        click.echo(header)
        click.echo("-" * len(header))
        for e in entries:
            ts = e.get("timestamp", "")[:19].replace("T", " ")
            actor = (e.get("actor") or "unknown")[:16]
            action = (e.get("action") or "")[:12]
            key = e.get("key") or "-"
            click.echo(f"{ts:<32} {actor:<16} {action:<12} {key}")


@audit_group.command("clear")
@click.option("--vault-dir", default=".", hidden=True)
@click.confirmation_option(prompt="Clear all audit log entries?")
def cmd_audit_clear(vault_dir):
    """Clear all audit log entries."""
    clear_log(vault_dir)
    click.echo("Audit log cleared.")
