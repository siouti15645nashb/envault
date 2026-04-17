"""CLI commands for variable pinning."""

import click
from envault.env_pin import pin_variable, unpin_variable, is_pinned, list_pinned, PinError


@click.group(name="pin")
def pin_group():
    """Pin variables to prevent accidental overwrites."""
    pass


@pin_group.command(name="add")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_pin_add(key, vault):
    """Pin a variable by KEY."""
    try:
        pin_variable(vault, key)
        click.echo(f"Pinned '{key}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pin_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_pin_remove(key, vault):
    """Unpin a variable by KEY."""
    try:
        unpin_variable(vault, key)
        click.echo(f"Unpinned '{key}'.")
    except PinError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pin_group.command(name="list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_pin_list(vault):
    """List all pinned variables."""
    pinned = list_pinned(vault)
    if not pinned:
        click.echo("No pinned variables.")
    else:
        for key in pinned:
            click.echo(key)


@pin_group.command(name="check")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_pin_check(key, vault):
    """Check if a variable is pinned."""
    if is_pinned(vault, key):
        click.echo(f"'{key}' is pinned.")
    else:
        click.echo(f"'{key}' is not pinned.")
