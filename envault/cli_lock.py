"""CLI commands for locking/unlocking vault variables."""

import click
from envault.env_lock import lock_variable, unlock_variable, get_locked, LockError

VAULT_FILE = ".envault"


@click.group(name="lock")
def lock_group():
    """Lock or unlock variables to prevent modification."""


@lock_group.command("add")
@click.argument("key")
@click.option("--vault", default=VAULT_FILE, show_default=True)
def cmd_lock_add(key, vault):
    """Lock a variable."""
    try:
        lock_variable(vault, key)
        click.echo(f"Variable '{key}' is now locked.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lock_group.command("remove")
@click.argument("key")
@click.option("--vault", default=VAULT_FILE, show_default=True)
def cmd_lock_remove(key, vault):
    """Unlock a variable."""
    try:
        unlock_variable(vault, key)
        click.echo(f"Variable '{key}' is now unlocked.")
    except LockError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lock_group.command("list")
@click.option("--vault", default=VAULT_FILE, show_default=True)
def cmd_lock_list(vault):
    """List all locked variables."""
    keys = get_locked(vault)
    if not keys:
        click.echo("No locked variables.")
    else:
        for k in keys:
            click.echo(k)
