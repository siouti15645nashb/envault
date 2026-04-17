"""CLI commands for managing variable visibility levels."""

import click
from envault.env_visibility import (
    set_visibility, get_visibility, remove_visibility,
    list_visibility, filter_by_level, VisibilityError, VALID_LEVELS
)


@click.group(name="visibility")
def visibility_group():
    """Manage variable visibility levels."""


@visibility_group.command(name="set")
@click.argument("key")
@click.argument("level", type=click.Choice(list(VALID_LEVELS)))
@click.option("--vault", default=".envault", show_default=True)
def cmd_visibility_set(key, level, vault):
    """Set visibility level for a variable."""
    try:
        set_visibility(vault, key, level)
        click.echo(f"Set '{key}' visibility to '{level}'.")
    except VisibilityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@visibility_group.command(name="get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_visibility_get(key, vault):
    """Get visibility level for a variable."""
    level = get_visibility(vault, key)
    click.echo(f"{key}: {level}")


@visibility_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_visibility_remove(key, vault):
    """Remove visibility setting for a variable (resets to default)."""
    remove_visibility(vault, key)
    click.echo(f"Removed visibility setting for '{key}'.")


@visibility_group.command(name="list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_visibility_list(vault):
    """List settings."""
    data = list_visibility(vault)
    if not data:
        click.echo("No visibility settings defined.")
        return
    for key, level in sorted(data.items()):
        click.echo(f"{key}: {level}")


@visibility_group.command(name="filter")
@click.argument("level", type=click.Choice(list(VALID_LEVELS)))
@click.option("--vault", default=".envault", show_default=True)
def cmd_visibility_filter(level, vault):
    """List variables with a specific visibility level."""
    try:
        keys = filter_by_level(vault, level)
    except VisibilityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if not keys:
        click.echo(f"No variables with level '{level}'.")
        return
    for key in sorted(keys):
        click.echo(key)
