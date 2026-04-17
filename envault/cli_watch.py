"""CLI commands for vault watch feature."""

import click
from envault.env_watch import watch_vault, WatchError


@click.group(name="watch")
def watch_group():
    """Watch vault for changes."""
    pass


@watch_group.command(name="start")
@click.argument("vault_path")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option("--interval", "-i", default=1.0, show_default=True, help="Poll interval in seconds")
def cmd_watch_start(vault_path: str, password: str, interval: float):
    """Watch VAULT_PATH and print changes as they occur."""

    def on_change(path, added, removed):
        if added:
            for key in sorted(added):
                click.echo(f"[+] Added:   {key}")
        if removed:
            for key in sorted(removed):
                click.echo(f"[-] Removed: {key}")

    try:
        click.echo(f"Watching {vault_path} (Ctrl+C to stop)...")
        watch_vault(vault_path, password, on_change, interval=interval)
    except WatchError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyboardInterrupt:
        click.echo("\nStopped watching.")
