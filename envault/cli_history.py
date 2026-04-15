"""CLI commands for variable change history."""

import os
import click
from envault.history import get_history, clear_history, HistoryError

VAULT_FILE = ".envault"


@click.group("history")
def history_group():
    """Commands for viewing variable change history."""
    pass


@history_group.command("log")
@click.argument("key", required=False, default=None)
@click.option("--vault", default=VAULT_FILE, help="Path to vault file.")
def cmd_history_log(key, vault):
    """Show change history, optionally filtered by KEY."""
    vault_dir = os.path.dirname(os.path.abspath(vault))
    try:
        entries = get_history(vault_dir, key=key)
    except HistoryError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if not entries:
        msg = f"No history for key '{key}'." if key else "No history recorded yet."
        click.echo(msg)
        return

    header = f"History for '{key}'" if key else "Full change history"
    click.echo(f"{header} ({len(entries)} entries):")
    click.echo("-" * 50)
    for entry in reversed(entries):
        ts = entry.get("timestamp", "?")
        actor = entry.get("actor", "unknown")
        action = entry.get("action", "?")
        k = entry.get("key", "?")
        click.echo(f"[{ts}] {actor}: {action} {k}")


@history_group.command("clear")
@click.option("--vault", default=VAULT_FILE, help="Path to vault file.")
@click.confirmation_option(prompt="Clear all history? This cannot be undone.")
def cmd_history_clear(vault):
    """Clear all change history."""
    vault_dir = os.path.dirname(os.path.abspath(vault))
    try:
        count = clear_history(vault_dir)
    except HistoryError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    click.echo(f"Cleared {count} history entries.")
