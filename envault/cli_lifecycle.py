"""CLI commands for lifecycle state management."""

import click
from envault.env_lifecycle import (
    set_lifecycle, get_lifecycle, remove_lifecycle,
    list_lifecycle, filter_by_state, VALID_STATES, LifecycleError
)


@click.group(name="lifecycle")
def lifecycle_group():
    """Manage variable lifecycle states."""


@lifecycle_group.command(name="set")
@click.argument("key")
@click.argument("state", type=click.Choice(VALID_STATES))
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_lifecycle_set(key, state, vault_dir):
    """Set lifecycle state for a variable."""
    try:
        set_lifecycle(vault_dir, key, state)
        click.echo(f"Set lifecycle of '{key}' to '{state}'.")
    except LifecycleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lifecycle_group.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_lifecycle_get(key, vault_dir):
    """Get lifecycle state of a variable."""
    state = get_lifecycle(vault_dir, key)
    click.echo(f"{key}: {state}")


@lifecycle_group.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_lifecycle_remove(key, vault_dir):
    """Remove lifecycle state entry for a variable."""
    remove_lifecycle(vault_dir, key)
    click.echo(f"Removed lifecycle state for '{key}'.")


@lifecycle_group.command(name="list")
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_lifecycle_list(vault_dir):
    """List all lifecycle states."""
    data = list_lifecycle(vault_dir)
    if not data:
        click.echo("No lifecycle states defined.")
        return
    for key, state in sorted(data.items()):
        click.echo(f"  {key}: {state}")


@lifecycle_group.command(name="filter")
@click.argument("state", type=click.Choice(VALID_STATES))
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_lifecycle_filter(state, vault_dir):
    """List variables in a given lifecycle state."""
    try:
        keys = filter_by_state(vault_dir, state)
        if not keys:
            click.echo(f"No variables in state '{state}'.")
            return
        for k in sorted(keys):
            click.echo(f"  {k}")
    except LifecycleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
